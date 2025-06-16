# 🗂️ Repo Whisperer

> Your friendly AI assistant for understanding GitHub repositories — just paste a repo URL, select a file, and ask questions!

## 🚀 Features

- 🌐 Paste any **public GitHub repo** URL to load its file structure.
- 🗃️ View a **TreeView** of all repository files.
- 🧠 Select a file, ask a question — get **context-aware answers** powered by **Cohere embeddings** and **Gemini/GPT**.
- 📚 Answers are formatted with markdown + code blocks and are easy to read.
- ⚡ Instant feedback using toast notifications.
- 📦 Uses **semantic chunking**, **vector similarity**, and **LLMs**.

---

<img width="1422" alt="Screenshot 2025-06-16 at 10 41 18 PM" src="https://github.com/user-attachments/assets/dab26bd5-6564-4225-bd3d-fc8f20a37a6e" />

The Output-

<div align="center">
  <img width="544" alt="Screenshot 2025-06-16 at 10 43 31 PM" src="https://github.com/user-attachments/assets/e260c3b9-1180-4bbd-871d-d5b652eff1a0" />
</div>

---


## 🛠️ Tech Stack

### Frontend
- **React** + **Vite**
- **Material UI (MUI)**
- **Framer Motion**
- **React Markdown** for rich formatting
- **React Syntax Highlighter** for code blocks
- **React Virtualized Autocomplete** for performance
- **Toastify** for notifications

### Backend
- **FastAPI** for serving endpoints
- **Cohere API** for vector embedding & chat
- **Gemini API** for answer generation
- **Scikit-learn** for cosine similarity
- **Requests**, **dotenv**, **NumPy**, etc.

---

## 🧪 How It Works

1. **User enters GitHub repo URL** → Frontend sends it to backend (`/fetch-files`)
2. Backend:
   - Extracts repo tree using `PyGitHub` or GitHub API
   - Returns list of files and tree structure
3. **User selects a file & asks a question**
4. Backend:
   - Fetches raw file content from GitHub
   - Splits code into chunks + embeds using **Cohere**
   - Embeddings saved to `data/` folder
   - Finds most relevant chunks using **cosine similarity**
   - Sends top chunks + user question to **Gemini/GPT**
   - Returns answer

---

## 📂 Folder Structure
```
Repo-Whisperer/
│
├── frontend/                  # React frontend (UI)
│   └── src/
│       └── App.jsx           # Core component (URL input, QnA interface)
│
├── backend/                  # FastAPI backend
│   ├── main.py               # API routes (/fetch-files, /ask)
│   ├── ingest/
│   │   ├── fetch_repo.py     # GitHub file listing
│   │   └── chunk_and_embed.py # Chunking + embedding logic
│   └── query/
│       └── ask_question.py   # Semantic search + LLM generation
│
├── data/                     # Stores JSON embeddings per file
└── README.md
```


## 🧠 Powered By

- Cohere – for embeddings, conversational model and advanced LLM responses
- GitHub REST API – for repo access
- FastAPI – for backend API

## 💡 Future Enhancements
- ✅ GitHub Auth (for private repos)
- 🔍 File-level search
- 🧪 Explain function/class on hover
- 🌍 Multi-language support

## 🙌 Author
Made with ❤️ by Sumedh
