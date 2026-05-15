# src/build_index.py
import os
import pickle
from sentence_transformers import SentenceTransformer
import faiss
from ingest import ingest_folder

EMB_MODEL = "all-MiniLM-L6-v2"
INDEX_DIR = "indexes"
INDEX_PATH = os.path.join(INDEX_DIR, "faiss.index")
META_PATH = os.path.join(INDEX_DIR, "meta.pkl")

def build_index(chunk_size=1000, overlap=200):
    print("[build] Loading and chunking PDFs...")
    chunks = ingest_folder(chunk_size=chunk_size, overlap=overlap)
    texts = [c["text"] for c in chunks]
    if not texts:
        raise ValueError("No chunks found. Put PDFs into data/books/")

    print(f"[build] Encoding {len(texts)} chunks with {EMB_MODEL} ...")
    model = SentenceTransformer(EMB_MODEL)
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    # normalize for cosine (IndexFlatIP)
    faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype("float32"))

    os.makedirs(INDEX_DIR, exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print("[build] Index & metadata saved.")
    print(" - index:", INDEX_PATH)
    print(" - meta:", META_PATH)

if __name__ == "__main__":
    build_index()
