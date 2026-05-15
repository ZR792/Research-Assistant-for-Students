# src/query_engine.py
import os
import pickle
import re
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Paths and models (change GEN_MODEL if you have stronger hardware)
INDEX_PATH = "indexes/faiss.index"
META_PATH = "indexes/meta.pkl"
EMB_MODEL = "all-MiniLM-L6-v2"
GEN_MODEL = "google/flan-t5-small"   # safe small model for CPU

CALC_PATTERN = re.compile(r"\[\[CALC:(.+?)\]\]")

# -------- safe calculator ----------
import ast, operator as op
operators = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.Pow: op.pow, ast.Mod: op.mod, ast.USub: lambda x: -x
}
def safe_eval(expr: str):
    node = ast.parse(expr, mode="eval").body
    def _eval(n):
        if isinstance(n, ast.Constant):  # Python 3.8+ node for numbers
            return n.value
        if isinstance(n, ast.Num):  # fallback
            return n.n
        if isinstance(n, ast.BinOp):
            return operators[type(n.op)](_eval(n.left), _eval(n.right))
        if isinstance(n, ast.UnaryOp):
            return operators[type(n.op)](_eval(n.operand))
        raise ValueError("Unsupported expression")
    return _eval(node)

# -------- init resources (call once and cache in UI) ----------
def init(index_path=INDEX_PATH, meta_path=META_PATH, emb_model=EMB_MODEL, gen_model=GEN_MODEL):
    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        raise FileNotFoundError("Index or meta not found. Run src/build_index.py first.")

    print("[init] Loading embedder...")
    embedder = SentenceTransformer(emb_model)

    print("[init] Loading FAISS index and meta...")
    index = faiss.read_index(index_path)
    with open(meta_path, "rb") as f:
        meta = pickle.load(f)

    print("[init] Loading generator model (this may be slow on first load)...")
    tokenizer = AutoTokenizer.from_pretrained(gen_model)
    gen_model = AutoModelForSeq2SeqLM.from_pretrained(gen_model)

    resources = {
        "embedder": embedder,
        "index": index,
        "meta": meta,
        "tokenizer": tokenizer,
        "gen_model": gen_model
    }
    print("[init] Resources ready.")
    return resources

# -------- retrieval with optional book filter ----------
def retrieve(query: str, resources, k: int = 4, book_filter: str = None, candidate_k: int = 50):
    embedder = resources["embedder"]
    index = resources["index"]
    meta = resources["meta"]

    q_emb = embedder.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)
    candidate_k = max(candidate_k, k*10)
    D, I = index.search(q_emb.astype("float32"), candidate_k)

    # form ordered unique candidate list, then filter by book_filter
    candidates = []
    for idx in I[0]:
        if idx < 0 or idx >= len(meta):
            continue
        candidates.append((idx, D[0][len(candidates)] if len(D[0])>len(candidates) else 0.0))

    # filter by book if requested
    selected = []
    if book_filter and book_filter.lower() != "all":
        for idx, _ in candidates:
            if meta[idx]["source"].lower().startswith(book_filter.lower()):
                selected.append(idx)
                if len(selected) >= k:
                    break
    # fallback: if not enough filtered, take top k overall
    if len(selected) < k:
        selected = [idx for idx, _ in candidates][:k]

    results = [meta[idx] for idx in selected]
    return results

# -------- prompt builder & generator ----------
def build_prompt(question, contexts):
    ctx_texts = ""
    for i, c in enumerate(contexts, start=1):
        ctx_texts += f"Context {i} (source: {c['source']}, page:{c['page']}):\n{c['text']}\n\n"
    prompt = (
        "You are a helpful student assistant. Use ONLY the context sections below to answer the question. "
        "If the answer is not present in the context, reply: 'I don't know based on the provided books.'\n\n"
        f"{ctx_texts}\nQuestion: {question}\nAnswer concisely; if you use facts cite the context number (e.g., [Context 1]). "
        "If you need to perform arithmetic, include it in the format [[CALC: expression]] and the app will compute it.\n"
    )
    return prompt

def generate_answer(question, contexts, resources, max_new_tokens=200):
    tokenizer = resources["tokenizer"]
    gen_model = resources["gen_model"]

    prompt = build_prompt(question, contexts)
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    out = gen_model.generate(**inputs, max_new_tokens=max_new_tokens, num_beams=4, early_stopping=True)
    answer = tokenizer.decode(out[0], skip_special_tokens=True)
    # handle calculator marker
    m = CALC_PATTERN.search(answer)
    if m:
        expr = m.group(1).strip()
        try:
            val = safe_eval(expr)
            answer = answer + f"\n\nCalculator result: {val}"
        except Exception as e:
            answer = answer + f"\n\nCalculator error: {e}"
    return answer

# -------- top-level wrapper ----------
def answer_query(user_input: str, resources, k: int = 4, book_filter: str = "All"):
    # direct calc command by user
    if user_input.strip().lower().startswith("calc:"):
        expr = user_input.split(":",1)[1].strip()
        try:
            return str(safe_eval(expr)), []
        except Exception as e:
            return f"Calc error: {e}", []

    contexts = retrieve(user_input, resources=resources, k=k, book_filter=book_filter)
    answer = generate_answer(user_input, contexts, resources)
    return answer, contexts

# quick example if run as script (for debugging)
if __name__ == "__main__":
    res = init()
    while True:
        q = input("Ask: ")
        if not q:
            break
        ans, ctxs = answer_query(q, res, k=4, book_filter="All")
        print("ANSWER:\n", ans)
        print("\nSOURCES:")
        for c in ctxs:
            print(f"- {c['source']} (page {c['page']})")
