# app/core/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration settings
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "YOUR-API-KEY")
INDEX_NAME = os.getenv("INDEX_NAME", "intelliscan-chatbot")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR-API-KEY")
