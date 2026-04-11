from playwright.sync_api import Page
from urllib.parse import urljoin
from typing import Optional
from .config_loader import get_selectors, get_env_vars
from .logger_config import get_logger

logger = get_logger(__name__)

class MoodleActions:
    def __init__(self, page: Page):
        self.page = page
        self.selectors = get_selectors()
        self.envs = get_env_vars()
        self._current_bank_url = None

    def buscar_questao(self, nome_questao: str, course_id: str = None, context_url: str = None) -> Optional[object]:
        """Busca pelo banco de questões do curso e retorna o locator do link de preview."""
        route = f"/question/edit.php?courseid={course_id}" if course_id else "/question/edit.php"
        q_url = context_url or urljoin(self.envs["url"], route)

        # Só navega se é a primeira vez ou se mudou de curso
        if self._current_bank_url != q_url:
            self.page.goto(q_url)
            self._current_bank_url = q_url
            self.page.wait_for_timeout(1500)

        # Busca pelo nome da questão no campo de pesquisa
        search_sel = self.selectors["question_bank"]["search_input"]
        if self.page.locator(search_sel).count() > 0:
            self.page.fill(search_sel, nome_questao)
            self.page.click("button[type='submit']")
            self.page.wait_for_timeout(1500)

        # Busca pela questão nos resultados
        rows = self.page.locator("table tbody tr").all()
        for row in rows:
            text = row.inner_text()
            if nome_questao.lower() in text.lower():
                # Pega diretamente o link de preview.php que fica escondido no dropdown "Editar"
                preview_link = row.locator("a[href*='preview.php']").first
                if preview_link.count() > 0:
                    return preview_link

        logger.warning(f"Questão '{nome_questao}' não localizada no banco de questões.")
        return None

    def interagir_alternativa_texto(self, texto_buscado: str, page_alvo: Page = None) -> bool:
        """Procura o texto nas alternativas e clica no radio correspondente.
        
        Estrutura HTML real:
        <div class="r0">
          <input type="radio" ... />
          <div data-region="answer-label">
            <span class="answernumber">a. </span>
            <div class="flex-fill ms-1">Texto da alternativa</div>
          </div>
        </div>
        """
        pg = page_alvo or self.page
        from .text_normalizer import normalize_text
        buscado = normalize_text(texto_buscado)

        # Percorre cada linha de alternativa (.r0 / .r1)
        rows = pg.locator(".answer .r0, .answer .r1").all()
        for row in rows:
            text_el = row.locator(".flex-fill")
            if text_el.count() > 0:
                texto_alt = normalize_text(text_el.first.inner_text())
                if buscado in texto_alt:
                    # Clica no input radio dentro desta mesma linha
                    radio = row.locator("input[type='radio']")
                    if radio.count() > 0:
                        radio.first.click()
                        return True
        return False

    def submeter_resposta(self, page_alvo: Page = None):
        """Clica em 'Enviar e finalizar' na pagina de preview."""
        pg = page_alvo or self.page
        # Seletor confirmado: input[name='finish']
        btn = pg.locator("input[name='finish']")
        if btn.count() > 0:
            btn.first.click()
            pg.wait_for_timeout(1500)

    def reiniciar_tentativa(self, page_alvo: Page = None):
        """Clica em 'Começar de novo' na pagina de preview."""
        pg = page_alvo or self.page
        # Seletor confirmado: input[name='restart']
        btn = pg.locator("input[name='restart']")
        if btn.count() > 0:
            btn.first.click()
            pg.wait_for_timeout(1000)
