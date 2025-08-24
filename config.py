import os
from dotenv import load_dotenv

load_dotenv()
PORT = int(os.getenv("PORT", 9090))
SIL_BASE = os.getenv("SIL_BASE", "http://localhost:8080")
PERSONA_FILE = os.getenv("PERSONA_FILE", "persona.json")
DRY_RUN = os.getenv("DRY_RUN", "1") == "1"
