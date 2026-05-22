# src/query_engine.py
import os
import pickle
import re
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ── Paths & model names ───────────────────────────────────────────────────────
INDEX_PATH = "indexes/faiss.index"
META_PATH  = "indexes/meta.pkl"
EMB_MODEL  = "all-MiniLM-L6-v2"
GEN_MODEL  = "google/flan-t5-small"   # swap to flan-t5-base if you have RAM

CALC_PATTERN = re.compile(r"\[\[CALC:(.+?)\]\]")

# ── Safe calculator ───────────────────────────────────────────────────────────
import ast, operator as op
_operators = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.Pow: op.pow, ast.Mod: op.mod, ast.USub: lambda x: -x
}
def safe_eval(expr: str):
    node = ast.parse(expr, mode="eval").body
    def _eval(n):
        if isinstance(n, ast.Constant): return n.value
        if isinstance(n, ast.Num):      return n.n
        if isinstance(n, ast.BinOp):
            return _operators[type(n.op)](_eval(n.left), _eval(n.right))
        if isinstance(n, ast.UnaryOp):
            return _operators[type(n.op)](_eval(n.operand))
        raise ValueError("Unsupported expression")
    return _eval(node)

# ── Init (load all resources once) ───────────────────────────────────────────
def init(index_path=INDEX_PATH, meta_path=META_PATH,
         emb_model=EMB_MODEL, gen_model=GEN_MODEL):
    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        raise FileNotFoundError(
            "Index or meta not found. Run `python src/build_index.py` first."
        )
    print("[init] Loading embedder...")
    embedder = SentenceTransformer(emb_model)

    print("[init] Loading FAISS index & meta...")
    index = faiss.read_index(index_path)
    with open(meta_path, "rb") as f:
        meta = pickle.load(f)

    print("[init] Loading generator model...")
    tokenizer  = AutoTokenizer.from_pretrained(gen_model)
    gen_model_ = AutoModelForSeq2SeqLM.from_pretrained(gen_model)

    resources = {
        "embedder":  embedder,
        "index":     index,
        "meta":      meta,
        "tokenizer": tokenizer,
        "gen_model": gen_model_,
        "index_path": index_path,
        "meta_path":  meta_path,
    }
    print("[init] Ready.")
    return resources

# ── Add new chunks to a live index (used after file upload) ──────────────────
def add_chunks_to_index(chunks, resources):
    """Encode new chunks and add them to the in-memory FAISS index + meta."""
    embedder = resources["embedder"]
    index    = resources["index"]
    meta     = resources["meta"]

    texts = [c["text"] for c in chunks]
    if not texts:
        return

    print(f"[index] Encoding {len(texts)} new chunks...")
    embeddings = embedder.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    faiss.normalize_L2(embeddings)
    index.add(embeddings.astype("float32"))
    meta.extend(chunks)
    print(f"[index] Index now has {index.ntotal} vectors.")

# ── Persist updated index to disk ────────────────────────────────────────────
def save_index(resources):
    index_path = resources.get("index_path", INDEX_PATH)
    meta_path  = resources.get("meta_path",  META_PATH)
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    faiss.write_index(resources["index"], index_path)
    with open(meta_path, "wb") as f:
        pickle.dump(resources["meta"], f)
    print(f"[index] Saved to {index_path}")

# ── Retrieval with optional book filter ──────────────────────────────────────
def retrieve(query, resources, k=4, book_filter=None, candidate_k=50):
    embedder = resources["embedder"]
    index    = resources["index"]
    meta     = resources["meta"]

    q_emb = embedder.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)
    candidate_k = max(candidate_k, k * 10)
    D, I = index.search(q_emb.astype("float32"), candidate_k)

    candidates = [(idx, D[0][i]) for i, idx in enumerate(I[0]) if 0 <= idx < len(meta)]

    selected = []
    if book_filter and book_filter.lower() not in ("all", "all books"):
        for idx, _ in candidates:
            if meta[idx]["source"].lower().startswith(book_filter.lower()):
                selected.append(idx)
                if len(selected) >= k:
                    break

    if len(selected) < k:
        selected = [idx for idx, _ in candidates][:k]

    return [meta[idx] for idx in selected]

# ── Prompt builder ────────────────────────────────────────────────────────────
def build_prompt(question, contexts):
    ctx_text = ""
    for i, c in enumerate(contexts, start=1):
        ctx_text += f"Context {i} (source: {c['source']}, page {c['page']}):\n{c['text']}\n\n"
    return (
        "You are a helpful student assistant. Use ONLY the context below to answer. "
        "If the answer is not in the context, say: 'I don't know based on the provided books.'\n\n"
        f"{ctx_text}\n"
        f"Question: {question}\n"
        "Answer concisely and cite context numbers (e.g. [Context 1]). "
        "For arithmetic embed it as [[CALC: expression]].\n"
    )

# ── Generator ─────────────────────────────────────────────────────────────────
def generate_answer(question, contexts, resources, max_new_tokens=200):
    tokenizer = resources["tokenizer"]
    gen_model = resources["gen_model"]
    prompt    = build_prompt(question, contexts)
    inputs    = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    out       = gen_model.generate(**inputs, max_new_tokens=max_new_tokens,
                                   num_beams=4, early_stopping=True)
    answer    = tokenizer.decode(out[0], skip_special_tokens=True)

    m = CALC_PATTERN.search(answer)
    if m:
        expr = m.group(1).strip()
        try:
            val    = safe_eval(expr)
            answer = answer + f"\n\n**Calculator:** {val}"
        except Exception as e:
            answer = answer + f"\n\n**Calc error:** {e}"
    return answer

# ── Top-level query wrapper ───────────────────────────────────────────────────
def answer_query(user_input, resources, k=4, book_filter="All"):
    if user_input.strip().lower().startswith("calc:"):
        expr = user_input.split(":", 1)[1].strip()
        try:
            return str(safe_eval(expr)), []
        except Exception as e:
            return f"Calc error: {e}", []

    contexts = retrieve(user_input, resources=resources, k=k, book_filter=book_filter)
    answer   = generate_answer(user_input, contexts, resources)
    return answer, contexts

# ── Debug CLI ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    res = init()
    while True:
        q = input("Ask: ")
        if not q:
            break
        ans, ctxs = answer_query(q, res)
        print("ANSWER:\n", ans)
        for c in ctxs:
            print(f"  - {c['source']} (p{c['page']})")