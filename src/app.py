# src/app.py
import streamlit as st
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(__file__))

from query_engine import init, answer_query, add_chunks_to_index, save_index
from ingest import ingest_file
from database import init_db, log_document, log_chat, get_all_documents, get_all_chats, get_stats

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp { background: #080c18; color: #dde3f5; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0c1120 0%, #0a0f1e 100%) !important;
    border-right: 1px solid #192038;
}
[data-testid="stSidebar"] * { color: #b0bcd8 !important; }

.hero { text-align: center; padding: 2.8rem 0 1.2rem; }
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(120deg, #5b9cf6 0%, #b388ff 45%, #40c4ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.1;
    letter-spacing: -1px;
}
.hero-sub { color: #4a5878; font-size: 0.92rem; margin-top: 0.5rem; }

.stat-card {
    background: linear-gradient(135deg, #0f1628 0%, #131c35 100%);
    border: 1px solid #1a2540;
    border-radius: 16px;
    padding: 1.2rem 1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #5b9cf6, #b388ff);
}
.stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #5b9cf6, #b388ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
.stat-label {
    font-size: 0.68rem;
    color: #3a4a6a;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.35rem;
    font-weight: 500;
}

.stTabs [data-baseweb="tab-list"] {
    background: #0c1120;
    border: 1px solid #192038;
    border-radius: 14px;
    padding: 5px;
    gap: 4px;
    margin-bottom: 1.5rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    padding: 0.6rem 1.6rem !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: #4a5878 !important;
    letter-spacing: 0.02em;
    flex: 1;
    text-align: center;
    justify-content: center;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #172040, #1a1840) !important;
    color: #5b9cf6 !important;
    border: 1px solid #2a3a6a !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

.stTextInput > div > div > input {
    background: #0c1120 !important;
    border: 1.5px solid #1a2540 !important;
    border-radius: 12px !important;
    color: #dde3f5 !important;
    padding: 0.75rem 1.1rem !important;
    font-size: 0.95rem !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: #5b9cf6 !important;
    box-shadow: 0 0 0 3px rgba(91,156,246,0.12) !important;
}
.stTextInput > div > div > input::placeholder { color: #2e3d5a !important; }

.stButton > button {
    background: linear-gradient(135deg, #5b9cf6 0%, #7c6fef 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    padding: 0.6rem 1.5rem !important;
    letter-spacing: 0.03em !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px rgba(91,156,246,0.3) !important;
}

.sec-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    color: #2e3d5a;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin: 1.4rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.sec-title::after { content: ''; flex: 1; height: 1px; background: #192038; }

.answer-bubble {
    background: linear-gradient(135deg, #0f1628 0%, #111e36 100%);
    border: 1px solid #1a2d50;
    border-left: 3px solid #5b9cf6;
    border-radius: 0 14px 14px 14px;
    padding: 1.4rem 1.6rem;
    margin: 0.6rem 0 1rem;
    line-height: 1.8;
    color: #c8d4f0;
    font-size: 0.94rem;
}

.question-bubble {
    background: linear-gradient(135deg, #172040, #1a1840);
    border: 1px solid #2a3a6a;
    border-radius: 14px 14px 0 14px;
    padding: 0.8rem 1.2rem;
    display: inline-block;
    max-width: 85%;
    color: #a0b4e8;
    font-size: 0.92rem;
    font-weight: 500;
    margin-bottom: 0.3rem;
}

.chip {
    display: inline-block;
    background: #0f1628;
    border: 1px solid #1e2f50;
    border-radius: 20px;
    padding: 0.22rem 0.8rem;
    font-size: 0.72rem;
    color: #5b7ab8;
    margin: 0.2rem 0.2rem 0.2rem 0;
}

.history-card {
    background: #0c1120;
    border: 1px solid #192038;
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.history-card:hover { border-color: #2a3a6a; }
.hc-question {
    font-family: 'Syne', sans-serif;
    font-size: 0.92rem;
    font-weight: 700;
    color: #7aabf7;
    margin-bottom: 0.7rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid #192038;
}
.hc-answer {
    color: #8a9dc0;
    font-size: 0.87rem;
    line-height: 1.7;
    padding: 0.6rem 0 0.7rem 0.9rem;
    border-left: 2px solid #1a2d50;
    margin-bottom: 0.8rem;
}
.hc-meta { font-size: 0.72rem; color: #2a3a5a; }
.hc-source { color: #3a5080; margin-left: 0.8rem; }

.doc-card {
    background: #0c1120;
    border: 1px solid #192038;
    border-radius: 12px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.55rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.empty-state { text-align: center; padding: 3.5rem 0; }
.empty-icon { font-size: 3rem; margin-bottom: 0.6rem; }
.empty-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #2e3d5a;
}
.empty-hint { font-size: 0.82rem; margin-top: 0.3rem; color: #1e2d48; }

.stDownloadButton > button {
    background: transparent !important;
    border: 1px solid #1a2d50 !important;
    color: #5b7ab8 !important;
    font-size: 0.8rem !important;
    padding: 0.35rem 1rem !important;
    border-radius: 8px !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #080c18; }
::-webkit-scrollbar-thumb { background: #192038; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── Init ───────────────────────────────────────────────────────────────────────
init_db()

@st.cache_resource
def load_resources():
    return init()

resources = load_resources()

if "chat_session" not in st.session_state:
    st.session_state.chat_session = []

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">📚 AI Research Assistant</div>
    <div class="hero-sub">Upload documents · Ask questions · Get cited answers instantly</div>
</div>
""", unsafe_allow_html=True)

# ── Stats ──────────────────────────────────────────────────────────────────────
stats = get_stats()
meta  = resources["meta"]
books = sorted(list({m["source"] for m in meta}))

c1, c2, c3, c4 = st.columns(4)
for col, num, label in [
    (c1, len(books),            "Books Loaded"),
    (c2, stats["total_docs"],   "Uploaded Docs"),
    (c3, stats["total_chats"],  "Questions Asked"),
    (c4, stats["total_chunks"], "Indexed Chunks"),
]:
    col.markdown(f"""
    <div class="stat-card">
        <div class="stat-num">{num}</div>
        <div class="stat-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.8rem'></div>", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    st.markdown("---")
    books_display = ["All Books"] + books
    book_choice = st.selectbox("🔍 Filter by book", books_display)
    k = st.slider("Chunks to retrieve (k)", 1, 8, 4)
    st.markdown("---")
    st.markdown("### 📖 Loaded Textbooks")
    for b in books:
        st.markdown(f"<div style='font-size:0.8rem;padding:0.2rem 0'>• {b}</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🗄️ Database")
    st.markdown(f"<div style='font-size:0.8rem'>📄 Docs: <b>{stats['total_docs']}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.8rem'>💬 Questions: <b>{stats['total_chats']}</b></div>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔄 Rebuild Index"):
        with st.spinner("Rebuilding..."):
            os.system("python src/build_index.py")
        st.success("Done!")
        st.rerun()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "💬   Ask a Question",
    "📂   Upload Document",
    "🕘   Chat History",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Ask
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="sec-title">Your Question</div>', unsafe_allow_html=True)

    query = st.text_input(
        "q", label_visibility="collapsed",
        placeholder="e.g.  What are ACID properties?     |     calc: 512 / 8"
    )

    col_ask, col_clear, _ = st.columns([1.2, 1, 5])
    with col_ask:
        ask_btn = st.button("Ask  →", use_container_width=True)
    with col_clear:
        if st.button("Clear", use_container_width=True):
            st.session_state.chat_session = []
            st.rerun()

    if ask_btn and query.strip():
        with st.spinner("Searching textbooks and generating answer..."):
            answer, contexts = answer_query(
                query, resources, k=k,
                book_filter=book_choice if book_choice != "All Books" else "All"
            )
        sources_str = "; ".join(
            f"{c['source']} p{c['page']}" for c in contexts
        ) if contexts else "calculator"
        log_chat(question=query, answer=answer, sources=sources_str)
        st.session_state.chat_session.append({"q": query, "a": answer, "contexts": contexts})

    if st.session_state.chat_session:
        for item in reversed(st.session_state.chat_session):
            st.markdown(
                f'<div style="text-align:right;margin-bottom:0.2rem">'
                f'<div class="question-bubble">🎓 {item["q"]}</div></div>',
                unsafe_allow_html=True
            )
            st.markdown('<div class="sec-title">Answer</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="answer-bubble">{item["a"]}</div>', unsafe_allow_html=True)

            if item["contexts"]:
                chips = "".join(
                    f'<span class="chip">📄 {c["source"]}  p.{c["page"]}</span>'
                    for c in item["contexts"]
                )
                st.markdown(f'<div style="margin:0.3rem 0 0.8rem">{chips}</div>', unsafe_allow_html=True)
                st.markdown('<div class="sec-title">Source Context</div>', unsafe_allow_html=True)
                for i, c in enumerate(item["contexts"], 1):
                    with st.expander(f"Context {i} · {c['source']}  (page {c['page']})"):
                        st.write(c["text"])

            combined = f"Question: {item['q']}\n\nAnswer:\n{item['a']}\n\nSources:\n"
            for i, c in enumerate(item["contexts"], 1):
                combined += f"{i}. {c['source']} (page {c['page']})\n{c['text']}\n\n"
            st.download_button(
                "⬇ Save answer as .txt", combined,
                file_name="answer.txt", mime="text/plain",
                key=f"dl_{id(item)}"
            )
            st.markdown("<hr style='border:none;border-top:1px solid #192038;margin:1.5rem 0'>",
                        unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🔍</div>
            <div class="empty-title">Ready to answer your questions</div>
            <div class="empty-hint">Type anything above — concepts, definitions, algorithms, or math</div>
            <div class="empty-hint" style="margin-top:0.4rem">
                Try: <i>What is the OSI model?</i> &nbsp;|&nbsp; <i>calc: 2**8</i>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Upload
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="sec-title">Upload a New Document</div>', unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#4a5878;font-size:0.88rem;margin-bottom:1rem'>"
        "Supported: <b>PDF, DOCX, PPTX, TXT</b>. "
        "The file is indexed immediately — then ask questions from it.</div>",
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Drop your file here", type=["pdf", "docx", "pptx", "txt"]
    )

    if uploaded_file:
        file_size_kb = len(uploaded_file.getvalue()) / 1024
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        icon = {"pdf": "📄", "docx": "📝", "pptx": "📊", "txt": "📃"}.get(ext.replace(".", ""), "📄")

        st.markdown(f"""
        <div style="background:#0c1120;border:1px solid #2a3a6a;border-radius:12px;
                    padding:1rem 1.2rem;margin:0.8rem 0;display:flex;align-items:center;gap:1rem">
            <span style="font-size:1.8rem">{icon}</span>
            <div style="flex:1">
                <div style="color:#a0b8e8;font-weight:600;font-size:0.95rem">{uploaded_file.name}</div>
                <div style="color:#3a4a6a;font-size:0.78rem;margin-top:0.2rem">
                    {file_size_kb:.1f} KB &nbsp;·&nbsp; {ext.upper().replace('.', '')}
                </div>
            </div>
            <div style="color:#5b9cf6;font-size:0.8rem;font-weight:600">Ready to index</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⚡ Index Document Now"):
            with st.spinner(f"Indexing {uploaded_file.name}..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                try:
                    chunks = ingest_file(tmp_path)
                    if not chunks:
                        st.error("❌ No text found. This may be a scanned/image-based file.")
                    else:
                        add_chunks_to_index(chunks, resources)
                        save_index(resources)
                        dest = os.path.join("data", "books", uploaded_file.name)
                        os.makedirs(os.path.dirname(dest), exist_ok=True)
                        shutil.copy(tmp_path, dest)
                        doc_id = log_document(
                            filename=uploaded_file.name,
                            file_type=ext.replace(".", "").upper(),
                            file_size_kb=file_size_kb,
                            num_chunks=len(chunks)
                        )
                        st.success(f"✅ Indexed **{len(chunks)} chunks** from **{uploaded_file.name}** (ID: {doc_id})")
                        st.info("Go to **Ask a Question** tab and start querying this document.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    os.unlink(tmp_path)

    st.markdown('<div class="sec-title">Previously Uploaded Documents</div>', unsafe_allow_html=True)
    docs = get_all_documents()
    if docs:
        for doc in docs:
            st.markdown(f"""
            <div class="doc-card">
                <span style="font-size:1.4rem">📄</span>
                <div style="flex:1">
                    <span style="color:#b8c8e8;font-size:0.9rem;font-weight:500">{doc['filename']}</span>
                    <span style="font-size:0.68rem;background:#172040;border:1px solid #2a3a6a;
                                 color:#5b9cf6;border-radius:6px;padding:0.1rem 0.5rem;
                                 margin-left:0.5rem">{doc['file_type']}</span>
                </div>
                <div style="text-align:right">
                    <div style="color:#5b9cf6;font-size:0.8rem;font-weight:600">{doc['num_chunks']} chunks</div>
                    <div style="color:#2a3a5a;font-size:0.72rem">{doc['uploaded_at'][:16]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📂</div>
            <div class="empty-title">No uploads yet</div>
            <div class="empty-hint">Upload a file above to get started</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — History
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    chats = get_all_chats(limit=50)

    if chats:
        st.markdown(
            f"<div style='color:#3a4a6a;font-size:0.82rem;margin-bottom:1.2rem'>"
            f"{len(chats)} questions stored in SQLite database</div>",
            unsafe_allow_html=True
        )
        for i, c in enumerate(chats, 1):
            # Safely get fields — no HTML entity rendering
            question  = c.get("question", "")
            answer    = c.get("answer", "")
            asked_at  = c.get("asked_at", "")[:16]
            sources   = c.get("sources", "") or ""
            doc_name  = c.get("doc_name", "") or ""

            # Build meta line as plain text parts
            meta_parts = [f"🕐 {asked_at}"]
            if sources and sources != "calculator":
                meta_parts.append(f"📄 {sources}")
            if doc_name:
                meta_parts.append(f"📁 {doc_name}")

            st.markdown(f"""
            <div class="history-card">
                <div class="hc-question">❓ {question}</div>
                <div class="hc-answer">{answer}</div>
                <div class="hc-meta" style="color:#2a3a5a;font-size:0.72rem">
                    {"&emsp;".join(meta_parts)}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🕘</div>
            <div class="empty-title">No history yet</div>
            <div class="empty-hint">Every question you ask is saved here automatically</div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem 0 0.8rem;font-size:0.75rem;color:#1e2d48;letter-spacing:0.05em">
    Sentence-Transformers &nbsp;·&nbsp; FAISS &nbsp;·&nbsp; Flan-T5 &nbsp;·&nbsp; SQLite &nbsp;·&nbsp; Streamlit
</div>
""", unsafe_allow_html=True)