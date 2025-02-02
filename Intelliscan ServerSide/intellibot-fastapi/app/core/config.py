# app/core/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration settings
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "c6c34888-213a-4c44-9445-659d84763224")
INDEX_NAME = os.getenv("INDEX_NAME", "intelliscan-chatbot")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyC7aHCqal7gJEDItUaQi-WMv-J4Z2uUA7Q")