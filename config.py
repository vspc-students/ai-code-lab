import os
from dotenv import load_dotenv

load_dotenv()

APP_TITLE = "AI Code Lab"
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "results.json")
