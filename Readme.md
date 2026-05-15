# 📘 AI Research Assistant for IT Students  

An AI-powered study companion designed to help IT and Computer Science students quickly access knowledge from standard textbooks. With features like intelligent search, context-based answers, and a built-in calculator, this assistant makes studying easier, faster, and more interactive.  

---

## Problem Statement  

Students often face these challenges while preparing for exams or doing assignments:  
- Searching through **multiple textbooks** for a single concept.  
- Spending too much time on **theory-heavy topics** without quick clarifications.  
- Difficulty in **connecting concepts** across subjects like Algorithms, Networking, Databases, and OS.  
- Switching between different resources for **maths or calculation-based problems**.  

This project solves these problems by creating a **centralized AI assistant** that:  
- Retrieves accurate explanations directly from textbooks.  
- Answers both conceptual and applied questions.  
- Supports solving **mathematical queries** with a built-in calculator.  
- Acts as a **virtual tutor** for IT students.  

---

## 🧑‍💻 What I Learned  

Through this project, I gained practical skills in:  
- **Natural Language Processing (NLP)** – splitting and embedding large documents.  
- **Vector Databases** – indexing and retrieving text chunks using FAISS.  
- **LangChain** – chaining tools like retrievers and calculators.  
- **Streamlit** – building an interactive and deployable UI.  
- **Model Deployment** – hosting on Streamlit Cloud with environment secrets.  
- **Best Practices** – project structuring, documentation, and scalability.  

---

## ⚙️ Tech Stack  

- **Frontend / UI**: [Streamlit](https://streamlit.io/)  
- **Backend / Logic**: [LangChain](https://www.langchain.com/)  
- **Embeddings**: [SentenceTransformers / OpenAI Embeddings]  
- **Vector Store**: [FAISS](https://faiss.ai/)  
- **Math Engine**: LangChain’s Calculator Tool  
- **Language Models**: OpenAI GPT / Hugging Face Transformers  
- **File Parsing**: PyPDF2, Pandas, NumPy  

---

## 📚 Books Included  

The assistant currently indexes knowledge from **10+ standard IT textbooks**, such as:  
- *Database System Concepts* – Silberschatz, Korth, Sudarshan  
- *Introduction to Algorithms* – Cormen et al.  
- *Operating System Concepts* – Silberschatz  
- *Computer Networking: A Top-Down Approach* – Kurose, Ross  
- *The Pragmatic Programmer* – Hunt, Thomas  
- *Clean Code* – Robert C. Martin  
- *Management* – Robbins & Coulter  
- *Mathematics for Computer Science* – Lehman et al.  
*(and more)*  

---

## 🖥️ Features  

- 📖 **Textbook Q&A** – Ask any concept-based question from included textbooks.  
- 🧮 **Math Tool** – Solve algebra, probability, linear algebra, and stats problems.  
- 🔎 **Contextual Search** – Retrieves relevant chunks instead of vague answers.  
- 🧠 **Multi-Subject Coverage** – Algorithms, OS, Networking, Databases, SE, Math, Management.  
- 🌐 **Web Deployment** – Accessible online through Streamlit Cloud.  

---
## 📂 Project Structure 
````
WEEK_05/
├── data/
│ ├── books/         # Collection of textbooks (PDFs)
│ │ ├── Clean code.pdf
│ │ ├── computer-networking.pdf
│ │ ├── Database System.pdf
│ │ ├── Discovering Computers.pdf
│ │ ├── Discrete_Maths.pdf
│ │ ├── Introduction to Algorithms.pdf
│ │ ├── Linear Algebra.pdf
│ │ ├── Management.pdf
│ │ └── Programatic Programmer.pdf
│ └── Sample_Text.md
│
├── indexes/         # Prebuilt FAISS index + metadata
│ ├── faiss.index
│ └── meta.pkl
│
├── src/              # Core application source code
│ ├── app.py          # Main Streamlit app
│ ├── build_index.py  # Script to build FAISS index from PDFs
│ ├── ingest.py       # Data ingestion / preprocessing
│ ├── query_engine.py # Handles querying and retrieval
│
├── requirements.txt 
├── Readme.md 
````

## 🚀 How to Run Locally  

1. Clone the repository  
   ```bash
   git clone https://github.com/ZR792/ai_fellowship.git
   cd week_05

2. Create virtual environment
``
python -m venv your-virtual-environment-name
``

 3. Install dependencies
 ``
pip install -r requirements.txt
 ``
 4. Run Main file
 ``
Streamlit run src/app.py
 ``
