from playwright.sync_api import Page, ElementHandle
from typing import List, Dict
from .config_loader import get_selectors
from .logger_config import get_logger

logger = get_logger(__name__)

def extract_texto_enunciado(page: Page) -> str:
    """Extrai o texto do enunciado da questão na página de preview."""
    # Tenta varios seletores comuns do Moodle
    for sel in [".qtext", ".formulation .qtext", ".formulation p", ".que .content .formulation"]:
        if page.locator(sel).count() > 0:
            return page.locator(sel).first.inner_text()
    return ""

def extract_alternativas(page: Page) -> List[Dict[str, str]]:
    """Extrai lista de alternativas da preview de questão do Moodle."""
    alts = []
    
    # Estrategia 1: Labels dentro de .answer (padrão mais universal)
    labels = page.locator(".answer label, .answeroptions label").all()
    if labels:
        for lbl in labels:
            text = lbl.inner_text().strip()
            if text:
                alts.append({"texto_moodle": text})
        if alts:
            return alts
    
    # Estrategia 2: Divs com classe d-flex dentro de .answer
    options = page.locator(".answer .d-flex, .answer > div").all()
    for opt in options:
        text = opt.inner_text().strip()
        if text:
            alts.append({"texto_moodle": text})
    if alts:
        return alts
            
    # Estrategia 3: Qualquer input radio/checkbox com texto proximo
    radios = page.locator("input[type='radio'], input[type='checkbox']").all()
    for radio in radios:
        parent = radio.locator("..")
        text = parent.inner_text().strip()
        if text:
            alts.append({"texto_moodle": text})
    
    return alts

def check_feedback_ok(page: Page) -> bool:
    """Verifica se o Moodle sinalizou resposta correta."""
    # Checa classes visuais de acerto
    if page.locator(".correct, .state.correct, .specificfeedback").count() > 0:
        texto_feedback = page.locator(".correct, .state, .specificfeedback, .grade").all_inner_texts()
        texto_junto = " ".join(texto_feedback).lower()
        if any(w in texto_junto for w in ["correta", "correto", "certo", "correct", "100"]):
            return True
    
    # Fallback visual: ícone de check
    if page.locator("i.fa-check, .icon.fa-check").count() > 0:
        return True
    return False

def check_feedback_erro(page: Page) -> bool:
    """Verifica se o Moodle sinalizou resposta incorreta."""
    if page.locator(".incorrect, .state.notcorrect, .specificfeedback").count() > 0:
        texto_feedback = page.locator(".incorrect, .state, .specificfeedback, .grade").all_inner_texts()
        texto_junto = " ".join(texto_feedback).lower()
        if any(w in texto_junto for w in ["incorreta", "incorreto", "errado", "incorrect", "0,00", "0.00"]):
            return True
    
    # Fallback visual: ícone de X
    if page.locator("i.fa-times, i.fa-xmark, .icon.fa-remove").count() > 0:
        return True
    return False
