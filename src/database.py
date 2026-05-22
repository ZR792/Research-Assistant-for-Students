# src/database.py
import sqlite3
import os
from datetime import datetime

DB_PATH = "data/research_assistant.db"

def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_size_kb REAL,
            num_chunks INTEGER DEFAULT 0,
            uploaded_at TEXT DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources TEXT,
            document_id INTEGER,
            asked_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (document_id) REFERENCES documents(id)
        )
    """)

    conn.commit()
    conn.close()

def log_document(filename, file_type, file_size_kb, num_chunks):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO documents (filename, file_type, file_size_kb, num_chunks)
        VALUES (?, ?, ?, ?)
    """, (filename, file_type, round(file_size_kb, 2), num_chunks))
    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return doc_id

def log_chat(question, answer, sources, document_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_history (question, answer, sources, document_id)
        VALUES (?, ?, ?, ?)
    """, (question, answer, sources, document_id))
    conn.commit()
    conn.close()

def get_all_documents():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents ORDER BY uploaded_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_chats(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ch.*, d.filename as doc_name
        FROM chat_history ch
        LEFT JOIN documents d ON ch.document_id = d.id
        ORDER BY ch.asked_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM documents")
    total_docs = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) as total FROM chat_history")
    total_chats = cursor.fetchone()["total"]
    cursor.execute("SELECT SUM(num_chunks) as total FROM documents")
    total_chunks = cursor.fetchone()["total"] or 0
    conn.close()
    return {"total_docs": total_docs, "total_chats": total_chats, "total_chunks": total_chunks}