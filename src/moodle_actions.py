from playwright.sync_api import Page, expect
from urllib.parse import urljoin
from typing import Dict
from .config_loader import get_selectors, get_env_vars
from .logger_config import get_logger

logger = get_logger(__name__)

class MoodleActions:
    def __init__(self, page: Page):
        self.page = page
        self.selectors = get_selectors()
        self.envs = get_env_vars()
        
    def buscar_questao(self, nome_questao: str, course_id: str = None, context_url: str = None) -> bool:
        """Busca pelo banco de questões do curso correspondente.
         Aviso: no caso real, requer entrar no Banco de Questoes ('/question/edit.php'). 
        """
        # Adiciona param courseid se ele existir
        route = f"/question/edit.php?courseid={course_id}" if course_id else "/question/edit.php"
        q_url = context_url or urljoin(self.envs["url"], route)
        self.page.goto(q_url)
        
        search_sel = self.selectors["question_bank"]["search_input"]
        btn_sel = self.selectors["question_bank"]["search_button"]
        
        # Muitos temas não tem campo pesquisa. É mockable fallback:
        if self.page.locator(search_sel).count() > 0:
            self.page.fill(search_sel, nome_questao)
            self.page.click(btn_sel)
            self.page.wait_for_timeout(2000) # Evita "networkidle" pendurar a requisição
        
        # Procurar o título pela listagem
        # Preferimos clicar no PREVIEW ('lupa') do exato item
        rows = self.page.locator(self.selectors["question_bank"]["question_row"]).all()
        for row in rows:
            text = row.inner_text()
            if nome_questao.lower() in text.lower():
                preview_btn = row.locator(self.selectors["question_bank"]["preview_action_icon"]).first
                if preview_btn:
                    # Precisamos prever popup vs mesma pagina.
                    # Moodle costuma abrir um popup ou _blank.
                    return preview_btn
        return None

    def interagir_alternativa_texto(self, texto_buscado: str, page_alvo: Page = None) -> bool:
        """Procura o texto na lista de alternativas exibida e clica no radio."""
        pg = page_alvo or self.page
        lbl_sel = self.selectors["preview_window"]["option_label"]
        opcoes = pg.locator(lbl_sel).all()
        
        from .text_normalizer import normalize_text
        buscado = normalize_text(texto_buscado)
        
        for op in opcoes:
            if buscado in normalize_text(op.inner_text()):
                op.click() # Clica e seleciona
                return True
        return False

    def submeter_resposta(self, page_alvo: Page = None):
        pg = page_alvo or self.page
        btn = self.selectors["preview_window"]["submit_button"]
        if pg.locator(btn).count() > 0:
             pg.locator(btn).first.click()
             pg.wait_for_timeout(1000)

    def reiniciar_tentativa(self, page_alvo: Page = None):
        pg = page_alvo or self.page
        btn = self.selectors["preview_window"]["start_again_button"]
        if pg.locator(btn).count() > 0:
            pg.locator(btn).first.click()
            pg.wait_for_timeout(800)
