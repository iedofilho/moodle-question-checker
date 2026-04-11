from playwright.sync_api import Page
from urllib.parse import urljoin
from typing import Optional, List
from .config_loader import get_selectors, get_env_vars
from .logger_config import get_logger

logger = get_logger(__name__)

class MoodleActions:
    def __init__(self, page: Page):
        self.page = page
        self.selectors = get_selectors()
        self.envs = get_env_vars()
        self._current_bank_url = None

    def buscar_questao(self, nome_questao: str, search_variants: List[str] = None,
                       course_id: str = None, context_url: str = None) -> Optional[str]:
        """Busca no banco de questoes e retorna a URL de preview.php direto.
        
        REALIDADE DO HTML (descoberta via source):
        - NAO existe campo de busca (input[name='questionname']) nesta versão.
        - O banco mostra TODAS as questoes (qperpage=1000) em uma tabela.
        - O nome da questao fica em: span.inplaceeditable[data-value="Nome"]
        - O link de preview fica no dropdown "Editar" de cada linha:
          a[href*='preview.php'] dentro do action-menu da mesma <tr>
        - Os nomes podem estar em dois formatos:
          "Fechada 01 - Aula 20" ou "Aula 20 - Fechada 01"
        """
        route = f"/question/edit.php?courseid={course_id}" if course_id else "/question/edit.php"
        q_url = context_url or urljoin(self.envs["url"], route)

        # Navega apenas 1x por sessao (cache de banco)
        if self._current_bank_url != q_url:
            self.page.goto(q_url)
            self._current_bank_url = q_url
            self.page.wait_for_load_state("domcontentloaded")
            self.page.wait_for_timeout(2000)
            
            # Clica em "Mostrar todos" se existir, para garantir que todas as questoes apareçam
            show_all = self.page.locator("button[data-filteraction='showall']")
            if show_all.count() > 0:
                try:
                    show_all.first.click()
                    self.page.wait_for_timeout(2000)
                except Exception:
                    pass

        # Monta lista de variantes de nome para busca flexível
        variants = search_variants or [nome_questao]
        
        # ESTRATÉGIA 1: Busca rápida via data-value nos span.inplaceeditable
        # Cada questao no banco tem: <span class="inplaceeditable" data-value="Nome Exato">
        for variant in variants:
            selector = f'span.inplaceeditable[data-value="{variant}"]'
            match = self.page.locator(selector)
            if match.count() > 0:
                logger.info(f"  -> Encontrada via data-value: '{variant}'")
                # Sobe pro <tr> pai e pega o link preview.php
                row = match.first.locator("xpath=ancestor::tr")
                preview = row.locator("a[href*='preview.php']")
                if preview.count() > 0:
                    href = preview.first.get_attribute("href")
                    return href
        
        # ESTRATÉGIA 2: Busca por texto parcial em todas as linhas da tabela
        # (para nomes que nao batem 100% com o data-value)
        logger.info(f"  -> Tentando busca por texto parcial...")
        all_editables = self.page.locator("span.inplaceeditable").all()
        for editable in all_editables:
            dv = editable.get_attribute("data-value") or ""
            for variant in variants:
                # Match case-insensitive e parcial
                if variant.lower() in dv.lower() or dv.lower() in variant.lower():
                    logger.info(f"  -> Match parcial: '{dv}' ~ '{variant}'")
                    row = editable.locator("xpath=ancestor::tr")
                    preview = row.locator("a[href*='preview.php']")
                    if preview.count() > 0:
                        href = preview.first.get_attribute("href")
                        return href
        
        # ESTRATÉGIA 3: Varredura classica por inner_text (fallback total)
        rows = self.page.locator("#categoryquestions tbody tr").all()
        for row in rows:
            try:
                text = row.inner_text()
            except Exception:
                continue
            for variant in variants:
                if variant.lower() in text.lower():
                    preview = row.locator("a[href*='preview.php']")
                    if preview.count() > 0:
                        href = preview.first.get_attribute("href")
                        logger.info(f"  -> Match por inner_text: '{variant}'")
                        return href

        logger.warning(f"Questao '{nome_questao}' nao localizada no banco de questoes.")
        return None

    def interagir_alternativa_texto(self, texto_buscado: str, page_alvo: Page = None) -> bool:
        """Procura o texto nas alternativas e clica no radio correspondente.
        
        Estrutura HTML real (confirmada do source):
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
