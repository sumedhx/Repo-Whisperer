# With cohere chatmodel
import os
import json
import time
import numpy as np
import cohere
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

load_dotenv()

# Init Cohere
COHERE_API_KEY = '2BoD7ySAZAsLs6Yf3cokKVaeiLfijnNeBMlZptmp'
co = cohere.Client(COHERE_API_KEY)

# Init Gemini
GEMINI_API_KEY = 'AIzaSyCfziDjvhQ3JKkDlDnVDw0CyO679CpxD-4'
genai.configure(api_key=GEMINI_API_KEY)

DATA_DIR = "data"  # Folder where chunk embeddings are stored


def embed_question(question):
    """
    Embed the user’s question using Cohere with input_type='search_query'
    """
    try:
        response = co.embed(
            texts=[question],
            model="embed-english-v3.0",
            input_type="search_query"
        )
        return list(response.embeddings)[0]
    except Exception as e:
        print(f"Error embedding question: {e}")
        return None


def load_all_embeddings(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filepath} not found.")
    all_chunks = []
    with open(filepath, "r") as f:
        data = json.load(f)
        for item in data:
            chunk = item["chunk"]
            embedding = item["embedding"]
            all_chunks.append((chunk, embedding))
    return all_chunks



def find_top_chunks(question_embedding, chunks_with_embeddings, top_k=3):
    """
    Compute cosine similarity between question and chunks.
    Return top_k most relevant chunks.
    """
    chunk_texts = [item[0] for item in chunks_with_embeddings]
    chunk_vectors = [item[1] for item in chunks_with_embeddings]

    # print("=======chunks_with_embeddings==", chunks_with_embeddings)
    similarities = cosine_similarity(
        [question_embedding],  # shape: (1, D)
        chunk_vectors          # shape: (N, D)
    )[0]

    # Get top_k indices
    top_indices = np.argsort(similarities)[-top_k:][::-1]

    top_chunks = [chunk_texts[i] for i in top_indices]
    print("Number top chunks: ",len(top_chunks))
    
    return top_chunks


def generate_answer_with_gemini(question, context_chunks):
    """
    Uses Cohere's Chat API to generate a response using the top context chunks.
    Keeps the same function name for compatibility.
    """
    try:
        # Construct the full prompt as context
        prompt = f"""
        You are a helpful coding assistant. Based on the following context from a codebase, answer the question clearly and concisely.
        
        Use markdown formatting (e.g. **bold headers**, bullet points) and include emojis where helpful to make the response more readable, engaging, and fun. Use emojis thoughtfully—at title, section headers, key points, and summaries-but be professional.

Context:
{context_chunks}

Question:
{question}
"""

        response = co.chat(
            message=question,
            preamble=prompt,
            model="command-r-large",
            temperature=0.3,
            chat_history=[],
        )
        
        print("=== The Response(response.text.strip) === ", response.text.strip())
        return response.text.strip()

    except Exception as e:
        return f"Error generating answer with Cohere Chat API: {e}"
        
        

def answer_question(user_question, filename):
    """
    Full pipeline:
    - Embed the question
    - Load all code chunk embeddings
    - Perform semantic search
    - Send top chunks + question to Gemini
    """
    
    print("======= ask_question.py operations ========")
    question_embedding = embed_question(user_question)
    if question_embedding is None:
        return "Error embedding your question."

    chunks = load_all_embeddings(filename)
    if not chunks:
        return "No code chunks found to search."

    top_chunks = find_top_chunks(question_embedding, chunks)
    context = "\n---\n".join(top_chunks)

    # Delay before calling Gemini to help with rate limits
    time.sleep(1)
    
    used_chucks=len(top_chunks)
    print('====', used_chucks)
    print("===Context===", context)
    # Generate final answer using Gemini
    return generate_answer_with_gemini(user_question, context),used_chucks



