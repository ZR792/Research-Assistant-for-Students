# src/ingest.py
import os
from PyPDF2 import PdfReader

def extract_pages_from_pdf(path):
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append({"text": text.strip(), "source": os.path.basename(path), "page": i})
    return pages

def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    L = len(text)
    if L == 0:
        return []
    while start < L:
        end = min(start + chunk_size, L)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def ingest_folder(folder="data/books", chunk_size=1000, overlap=200):
    all_chunks = []
    for fname in sorted(os.listdir(folder)):
        if not fname.lower().endswith(".pdf"):
            continue
        path = os.path.join(folder, fname)
        print(f"[ingest] Reading {path}")
        pages = extract_pages_from_pdf(path)
        for p in pages:
            subchunks = chunk_text(p["text"], chunk_size=chunk_size, overlap=overlap)
            for n, sc in enumerate(subchunks, start=1):
                all_chunks.append({
                    "text": sc,
                    "source": p["source"],
                    "page": p["page"],
                    "chunk_id": f"{p['source']}_p{p['page']}_c{n}"
                })
    print(f"[ingest] Ingested {len(all_chunks)} chunks from PDFs in {folder}")
    return all_chunks

if __name__ == "__main__":
    chunks = ingest_folder()
    print("Sample chunk:", chunks[0] if chunks else "No chunks found")
