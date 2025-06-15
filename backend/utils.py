# backend/utils.py

def embedding_filename(repo_name, file_path):
    """
    Sanitizes filename for saving embedding JSON file.
    """
    safe_file_path = file_path.replace('/', '_').replace('\\', '_')
    return f"{repo_name}_{safe_file_path}.json"
