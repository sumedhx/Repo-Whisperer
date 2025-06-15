# Using some filter 

import os
import json
import cohere
from backend.ingest.token_utils import chunk_text
from utils import embedding_filename

COHERE_API_KEY = '2BoD7ySAZAsLs6Yf3cokKVaeiLfijnNeBMlZptmp'
co = cohere.Client(COHERE_API_KEY)

def preprocess_chunks(chunks):
    """
    Filter out empty or trivial chunks and deduplicate them to reduce embedding usage.
    """
    filtered = []
    seen = set()

    for chunk in chunks:
        # Remove chunks that are empty or too short (adjust threshold as needed)
        if not chunk.strip() or len(chunk.strip()) < 30:
            continue
        # Optional: skip chunks with mostly non-alphanumeric chars (e.g., big comments)
        if sum(c.isalnum() for c in chunk) < 10:
            continue

        # Deduplicate
        if chunk not in seen:
            seen.add(chunk)
            filtered.append(chunk)

    return filtered

def embed_chunks(chunks):
    """
    Takes a list of string chunks and returns list of embeddings using Cohere.
    """
    if not chunks:
        return []

    try:
        # Cohere allows batch embedding, send all chunks in one call
        response = co.embed(
            texts=chunks,
            model="embed-english-v3.0",
            input_type="search_document"
        )
        return response.embeddings
    except Exception as e:
        print(f"Error embedding chunks with Cohere: {e}")
        return None

def chunk_and_embed_file(repo_name, file_path, file_content):
    print("======= chunk_and_embed.py operations ========")
    print(f"Processing {file_path}...")

    os.makedirs("data", exist_ok=True)
    filename = embedding_filename(repo_name, file_path)
    filepath = os.path.join("data", filename)

    # Check if embeddings file already exists; if yes, skip re-embedding
    if os.path.exists(filepath):
        print(f"Embedding for {file_path} already exists at {filepath}. Skipping embedding.")
        with open(filepath, "r") as f:
            existing_data = json.load(f)
        return len(existing_data)

    # Call chunk_text with a larger chunk size if your function supports it,
    # or modify your chunk_text to increase chunk size (e.g., from 500 to 1000 tokens)
    chunks = chunk_text(file_content)  

    if not chunks:
        print(f"No chunks generated for {file_path}. Skipping.")
        return 0

    # Preprocess chunks to reduce trivial or duplicate data before embedding
    chunks = preprocess_chunks(chunks)
    if not chunks:
        print(f"No valid chunks after preprocessing for {file_path}. Skipping.")
        return 0

    embeddings = embed_chunks(chunks)
    if not embeddings:
        print("No embeddings returned. Aborting.")
        return 0

    chunk_embeddings = []
    for chunk, embedding in zip(chunks, embeddings):
        chunk_embeddings.append({
            "chunk": chunk,
            "embedding": embedding
        })
    chunk_count = len(chunk_embeddings)
    print("+ Chunk Create : ", chunk_count)

    with open(filepath, "w") as f:
        json.dump(chunk_embeddings, f, indent=2)

    print(f"Saved embeddings for {file_path} to {filepath}")
    
    return chunk_count





# Using some filter 
# import os
# import json
# import cohere
# from ingest.token_utils import chunk_text
# from utils import embedding_filename

# COHERE_API_KEY = '2BoD7ySAZAsLs6Yf3cokKVaeiLfijnNeBMlZptmp'
# co = cohere.Client(COHERE_API_KEY)

# def preprocess_chunks(chunks):
#     """
#     Filter out empty or trivial chunks and deduplicate them to reduce embedding usage.
#     """
#     filtered = []
#     seen = set()

#     for chunk in chunks:
#         # Remove chunks that are empty or too short (adjust threshold as needed)
#         if not chunk.strip() or len(chunk.strip()) < 30:
#             continue
#         # Optional: skip chunks with mostly non-alphanumeric chars (e.g., big comments)
#         if sum(c.isalnum() for c in chunk) < 10:
#             continue

#         # Deduplicate
#         if chunk not in seen:
#             seen.add(chunk)
#             filtered.append(chunk)

#     return filtered

# def embed_chunks(chunks):
#     """
#     Takes a list of string chunks and returns list of embeddings using Cohere.
#     """
#     if not chunks:
#         return []

#     try:
#         # Cohere allows batch embedding, send all chunks in one call
#         response = co.embed(
#             texts=chunks,
#             model="embed-english-v3.0",
#             input_type="search_document"
#         )
#         return response.embeddings
#     except Exception as e:
#         print(f"Error embedding chunks with Cohere: {e}")
#         return None

# def chunk_and_embed_file(repo_name, file_path, file_content):
#     print("======= chunk_and_embed.py operations ========")
#     print(f"Processing {file_path}...")

#     # Call chunk_text with a larger chunk size if your function supports it,
#     # or modify your chunk_text to increase chunk size (e.g., from 500 to 1000 tokens)
#     chunks = chunk_text(file_content)  

#     if not chunks:
#         print(f"No chunks generated for {file_path}. Skipping.")
#         return

#     # Preprocess chunks to reduce trivial or duplicate data before embedding
#     chunks = preprocess_chunks(chunks)
#     if not chunks:
#         print(f"No valid chunks after preprocessing for {file_path}. Skipping.")
#         return

#     embeddings = embed_chunks(chunks)
#     if not embeddings:
#         print("No embeddings returned. Aborting.")
#         return

#     chunk_count = 0
#     chunk_embeddings = []
#     for chunk, embedding in zip(chunks, embeddings):
#         chunk_embeddings.append({
#             "chunk": chunk,
#             "embedding": embedding
#         })
#         chunk_count = chunk_count + 1
#     print("+ Chunk Create : ",chunk_count)

#     os.makedirs("data", exist_ok=True)
#     filename = embedding_filename(repo_name, file_path)
#     filepath = os.path.join("data", filename)

#     with open(filepath, "w") as f:
#         json.dump(chunk_embeddings, f, indent=2)

#     print(f"Saved embeddings for {file_path} to {filepath}")
    
#     return chunk_count

