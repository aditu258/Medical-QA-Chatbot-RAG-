# 🩺 Medical-QA-Chatbot-RAG

An end-to-end Retrieval-Augmented Generation (RAG) medical QA chatbot built with Flask, Pinecone (vector DB), and Gemini-like LLM/embeddings.

✨ What this repo does
- Ingests clinical/medical documents (PDF), creates embeddings, stores vectors in Pinecone, and serves a small Flask chat UI that retrieves relevant context and generates answers with an LLM.

🗺️ Architecture diagram

- Click to open (local file — opens on your machine):

[Open architecture diagram (local)](file:///C:/Users/Lenovo/Downloads/Untitled%20diagram%20_%20Mermaid%20Chart-2025-08-28-170844.svg)

- If you want the diagram available to others from the repo, copy the SVG into `docs/diagram.svg` (example PowerShell command):

```powershell
mkdir -Force ".\docs"; Copy-Item -Path "C:\Users\Lenovo\Downloads\Untitled diagram _ Mermaid Chart-2025-08-28-170844.svg" -Destination ".\docs\diagram.svg" -Force
```

After copying, this relative link will work on GitHub and locally:

[Open architecture diagram (repo)](docs/diagram.svg)

🧭 Quick start (local)

1. Create Python environment (conda or venv)

```powershell
# conda
conda create -n medibot python=3.10 -y; conda activate medibot

# or venv
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

# 🩺 Medical-QA-Chatbot-RAG

Simple, focused README that explains what the project is and how to run it locally.

What this project does
- Builds a Retrieval-Augmented Generation (RAG) pipeline for medical Q&A:
	- Ingests documents (PDF) and splits into chunks
	- Creates embeddings and stores them in a vector DB (Pinecone)
	- Serves a Flask web UI (`templates/chat.html`) that retrieves relevant chunks and asks an LLM (via `GEMINI_API_KEY`) to generate answers

Quick start (copy-paste)

1) Create Python environment

```powershell
# conda
conda create -n medibot python=3.10 -y; conda activate medibot

# or venv
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2) Install dependencies

```powershell
pip install -r requirements.txt
```

3) Add credentials (DO NOT COMMIT)

Create a `.env` file in the project root with:

```ini
PINECONE_API_KEY="your_pinecone_api_key"
GEMINI_API_KEY="your_llm_or_embedding_key"
FLASK_SECRET_KEY="a-secret-for-sessions"
```

4) Ingest documents into Pinecone

```powershell
python store_index.py
```

5) Run the app

```powershell
python app.py
```

Open http://127.0.0.1:5000/ and ask questions.

Key files (quick mapping)
- `app.py` — Flask server and endpoints
- `store_index.py` — ingestion pipeline (PDF -> chunks -> embeddings -> upsert)
- `src/helper.py` — chunking, embedding, retrieval, postprocess utilities
- `src/prompt.py`, `template.py` — prompt templates
- `Data/Medical_book.pdf` — sample document
- `templates/chat.html`, `static/style.css` — frontend UI

Security notes
- Do NOT commit `.env` or API keys. Add `.env` to `.gitignore`.
- Rotate keys if they were exposed.

Need help?
- I can: add `docs/diagram.svg` (you can copy your SVG into `docs/`), create a small smoke test script, or add a `--dry-run` mode to `store_index.py` so ingestion runs without real API calls. Tell me which you want next.

---
Updated README: concise, beginner-friendly, and ready to share.
