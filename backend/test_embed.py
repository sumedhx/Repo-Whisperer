# test_embed.py

from ingest.chunk_and_embed import chunk_and_embed_file

repo_name = "LinkedIn-Content-Extractor"
file_path = "main.py"
file_content = open("main.py").read()  # or from API response

chunk_and_embed_file(repo_name, file_path, file_content)
