import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openai/gpt-oss-120b"
)