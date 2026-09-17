import hashlib
import json
import os
import uuid
from config import DATA_FILE


def _ensure_data_file():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=2)


def get_or_create_participant():
    # Anonymous research identity. No name, email, phone or other PII is stored.
    token = uuid.uuid4().hex
    return "P-" + hashlib.sha256(token.encode()).hexdigest()[:6].upper()


def load_results():
    _ensure_data_file()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_result(result):
    results = load_results()
    results.append(result)
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)
