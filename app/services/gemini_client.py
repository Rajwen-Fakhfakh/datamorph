import os

from dotenv import load_dotenv
from google import genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Modèle configurable via .env (ex: GEMINI_MODEL=gemini-3.8-flash)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

client = genai.Client(api_key=GEMINI_API_KEY)
