import re
import unicodedata

def normalize_text(text: str, strict: bool = False) -> str:
    """Normaliza texto para comparacao. Se restrict=False, limpa acentos e converte minúsculo."""
    if text is None:
        return ""
    # Remove HTML tags simples se houver
    text = re.sub(r'<[^>]*>', ' ', text)
    # Collapse whitespaces
    text = " ".join(text.split())
    
    if not strict:
        text = text.lower()
        # Remove acentos
        text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    
    return text.strip()
