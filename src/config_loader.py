import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def load_json(filepath: str) -> dict:
    file_path = Path(filepath)
    if not file_path.exists():
        raise FileNotFoundError(f"Configuração ausente: {filepath}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_settings():
    base = Path(__file__).parent.parent
    return load_json(base / "config" / "settings.json")

def get_selectors():
    base = Path(__file__).parent.parent
    return load_json(base / "config" / "selectors.json")

def get_env_vars():
    url = os.getenv("MOODLE_URL")
    if not url:
        raise ValueError("Variável MOODLE_URL não fornecida no .env")
        
    return {
        "url": url,
        # Força headless false porque o login manual é obrigatoriamente visual
        "headless": False, 
        "slow_mo": int(os.getenv("PLAYWRIGHT_SLOW_MO", "500"))
    }
