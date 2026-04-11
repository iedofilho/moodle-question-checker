from playwright.sync_api import Page
from typing import List, Dict
from .logger_config import get_logger

logger = get_logger(__name__)

def extract_texto_enunciado(page: Page) -> str:
    """Extrai o texto do enunciado da questão na página de preview."""
    # Seletor confirmado pelo HTML real: div.qtext
    if page.locator(".qtext").count() > 0:
        return page.locator(".qtext").first.inner_text()
    return ""

def extract_alternativas(page: Page) -> List[Dict[str, str]]:
    """Extrai lista de alternativas da preview de questão do Moodle.
    
    Estrutura HTML real da Fundace (Moodle 4+ / Lambda2):
    <div class="answer">
      <div class="r0">
        <input type="radio" ... />
        <div class="d-flex w-auto" data-region="answer-label">
          <span class="answernumber">a. </span>
          <div class="flex-fill ms-1">Texto da alternativa</div>
        </div>
      </div>
      ...
    </div>
    """
    alts = []
    
    # Cada alternativa vive dentro de .r0 ou .r1 na div .answer
    rows = page.locator(".answer .r0, .answer .r1").all()
    for row in rows:
        # O texto limpo da alternativa (sem a letra "a. ", "b. " etc) mora em .flex-fill
        text_el = row.locator(".flex-fill")
        if text_el.count() > 0:
            text = text_el.first.inner_text().strip()
        else:
            # Fallback: pegar o label inteiro
            label_el = row.locator("[data-region='answer-label']")
            text = label_el.first.inner_text().strip() if label_el.count() > 0 else row.inner_text().strip()
        
        if text:
            alts.append({"texto_moodle": text})
    
    return alts

def check_feedback_ok(page: Page) -> bool:
    """Verifica se o Moodle sinalizou resposta correta após submissão."""
    # Classe .correct aparece no div da questão quando a resposta é certa
    if page.locator(".correct").count() > 0:
        return True
    # Texto de feedback
    if page.locator(".specificfeedback").count() > 0:
        texto = page.locator(".specificfeedback").first.inner_text().lower()
        if any(w in texto for w in ["correta", "correto", "certo", "correct"]):
            return True
    # Nota máxima no grade area
    if page.locator(".grade").count() > 0:
        grade_text = page.locator(".grade").first.inner_text()
        if "1,00" in grade_text or "1.00" in grade_text:
            return True
    return False

def check_feedback_erro(page: Page) -> bool:
    """Verifica se o Moodle sinalizou resposta incorreta após submissão."""
    if page.locator(".incorrect").count() > 0:
        return True
    if page.locator(".specificfeedback").count() > 0:
        texto = page.locator(".specificfeedback").first.inner_text().lower()
        if any(w in texto for w in ["incorreta", "incorreto", "errado", "incorrect"]):
            return True
    if page.locator(".grade").count() > 0:
        grade_text = page.locator(".grade").first.inner_text()
        if "0,00" in grade_text or "0.00" in grade_text:
            return True
    return False
