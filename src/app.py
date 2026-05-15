# src/app.py
import streamlit as st
import os
import pickle
from query_engine import init, answer_query

st.set_page_config(page_title="Student Research Assistant", layout="wide")
st.title("📚 AI Research Companion for IT Students")

# --------------- load resources and cached ---------------
@st.cache_resource
def load_resources():
    return init()

resources = load_resources()

# get available books from meta
meta = resources["meta"]
books = sorted(list({m["source"] for m in meta}))
books_display = ["All"] + books

# Sidebar
with st.sidebar:
    st.header("Data & Controls")
    st.write(f"Loaded books ({len(books)}):")
    for b in books:
        st.write("- " + b)
    st.write("---")
    book_choice = st.selectbox("Search in", books_display, index=0)
    k = st.slider("Number of retrieved chunks (k)", min_value=1, max_value=8, value=4)
    st.markdown("**Index / Data**")
    st.write("To add new books: put PDFs in `data/books/` and click Rebuild index.")
    if st.button("Rebuild index"):
        st.warning("Rebuilding index — this may take a while. Run `python src/build_index.py` in terminal if it hangs.")
        os.system("python src/build_index.py")
        st.experimental_rerun()

# Main
st.markdown("Ask questions from the loaded textbooks. Tip: type `calc: 23*45` to use the calculator.")
query = st.text_input("Ask a question", placeholder="e.g., What is an eigenvalue?")

if st.button("Ask") and query.strip():
    with st.spinner("Searching and generating answer..."):
        answer, contexts = answer_query(query, resources, k=k, book_filter=book_choice)
    st.subheader("Answer")
    st.write(answer)

    # show contexts in expanders
    st.subheader("Retrieved Contexts")
    for i, c in enumerate(contexts, start=1):
        with st.expander(f"Context {i} — {c['source']} (page {c['page']})"):
            st.write(c["text"])

    # Download combined result
    combined = f"Question: {query}\n\nAnswer:\n{answer}\n\nSources:\n"
    for i, c in enumerate(contexts, start=1):
        combined += f"Context {i}: {c['source']} (page {c['page']})\n{c['text']}\n\n"

    st.download_button("Download result (.txt)", combined, file_name="qa_result.txt", mime="text/plain")

# Footer
st.markdown("---")
st.caption("Built with Sentence-Transformers, FAISS, Flan-T5 (local). Put scanned PDFs through OCR before ingestion.")
