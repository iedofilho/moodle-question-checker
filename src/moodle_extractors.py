from playwright.sync_api import Page, ElementHandle
from typing import List, Dict
from .config_loader import get_selectors

def extract_texto_enunciado(page: Page) -> str:
    sel = get_selectors()["preview_window"]["question_text"]
    if page.locator(sel).count() > 0:
        return page.locator(sel).first.inner_text()
    return ""

def extract_alternativas(page: Page) -> List[Dict[str, str]]:
    """Extrai lista do Moodle e devolve as chaves visando bater seletor HTML ou texto_limpo."""
    sel = get_selectors()["preview_window"]["answer_option"]
    lbl_sel = get_selectors()["preview_window"]["option_label"]
    
    elements = page.locator(sel).all()
    alts = []
    
    for _, el in enumerate(elements):
        # Cada Moodle coloca a resposta (a, b, c) de uma forma, então buscamos a prop
        # Aqui pegamos o label total e usaremos normalização
        text = el.locator(lbl_sel).inner_text() if el.locator(lbl_sel).count() > 0 else el.inner_text()
        input_loc = el.locator("input").first
        val_id = input_loc.get_attribute("id") if input_loc else None
        
        alts.append({
            "texto_moodle": text,
            "el_locator": el
        })
    return alts

def check_feedback_ok(page: Page) -> bool:
    sel_feed = get_selectors()["preview_window"]["feedback_correct_area"]
    if page.locator(sel_feed).count() > 0:
        texto = page.locator(sel_feed).inner_text().lower()
        # Validação simples que pode ser expandida em settings
        return "correta" in texto.lower() or "certo" in texto.lower() or "correto" in texto.lower()
    
    # Checar class de mark correct
    if page.locator(".correct").count() > 0 or page.locator("i.fa-check").count() > 0:
         return True
    return False

def check_feedback_erro(page: Page) -> bool:
    sel_feed = get_selectors()["preview_window"]["feedback_correct_area"]
    if page.locator(sel_feed).count() > 0:
        texto = page.locator(sel_feed).inner_text().lower()
        return "incorreta" in texto.lower() or "errado" in texto.lower()
    
    if page.locator(".incorrect").count() > 0 or page.locator("i.fa-times").count() > 0:
         return True
    return False
