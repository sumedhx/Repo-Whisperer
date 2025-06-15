# backend/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from backend.ingest.fetch_repo import list_repo_files
from backend.ingest.chunk_and_embed import chunk_and_embed_file
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.query.ask_question import answer_question, generate_answer_with_gemini
import requests

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


app = FastAPI()

origins = [
    "http://localhost:5173",
  "https://repo-whisperer-rrrp.vercel.app/"  # your frontend origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # allow this origin only; or ["*"] for all origins
    allow_credentials=True,  # if you use cookies or authorization headers
    allow_methods=["*"],  # allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # allow all headers
)

class FetchFilesRequest(BaseModel):
    owner: str
    repo: str
    
class AskRequest(BaseModel):
    owner: str
    repo: str
    filePath: str
    question: str

# Serve frontend static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")

# For frontend routing (React Router fallback)
@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    path_to_file = os.path.join("static", full_path)
    if os.path.isfile(path_to_file):
        return FileResponse(path_to_file)
    else:
        return FileResponse("static/index.html")

@app.post("/fetch-files")
async def fetch_files(req: FetchFilesRequest):
    try:
        files, repoTree = list_repo_files(req.owner, req.repo)
        return {"files": files, "repoTree": repoTree}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(req: AskRequest):
    try:
        # Step 1: Fetch raw file content from GitHub
        url = f"https://raw.githubusercontent.com/{req.owner}/{req.repo}/main/{req.filePath}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch file content: {response.status_code}")
        file_content = response.text

        # Step 2: Chunk + Embed the file
        # chunk_and_embed_file(req.repo, req.filePath, file_content)
        chunk_count = chunk_and_embed_file(req.repo, req.filePath, file_content)

        # Step 3: Perform semantic search over chunks
        context_chunks = answer_question(req.question)

        # Step 4: Send top chunks + question to Gemini to generate final answer
        final_answer = generate_answer_with_gemini(req.question, context_chunks)
        
        used_chucks = len(context_chunks)

        return {"answer": final_answer,"chunk_count": chunk_count, "used_chucks": used_chucks}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
