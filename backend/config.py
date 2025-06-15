# backend/config.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Or hardcode for now

genai.configure(api_key=GOOGLE_API_KEY)
