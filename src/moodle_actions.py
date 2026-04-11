from playwright.sync_api import Page, expect
from urllib.parse import urljoin
from typing import Dict, Optional
from .config_loader import get_selectors, get_env_vars
from .logger_config import get_logger

logger = get_logger(__name__)

class MoodleActions:
    def __init__(self, page: Page):
        self.page = page
        self.selectors = get_selectors()
        self.envs = get_env_vars()
        self._current_bank_url = None  # Cache para evitar recarregamento da mesma pagina
        
    def buscar_questao(self, nome_questao: str, course_id: str = None, context_url: str = None) -> Optional[object]:
        """Busca pelo banco de questões do curso correspondente.
         Aviso: no caso real, requer entrar no Banco de Questoes ('/question/edit.php'). 
        """
        # Adiciona param courseid se ele existir
        route = f"/question/edit.php?courseid={course_id}" if course_id else "/question/edit.php"
        q_url = context_url or urljoin(self.envs["url"], route)
        
        # Só navega se é a primeira vez ou se mudou de curso
        if self._current_bank_url != q_url:
            self.page.goto(q_url)
            self._current_bank_url = q_url
            self.page.wait_for_timeout(1500)
        
        # Busca pelo nome da questão
        search_sel = self.selectors["question_bank"]["search_input"]
        btn_sel = self.selectors["question_bank"]["search_button"]
        
        if self.page.locator(search_sel).count() > 0:
            self.page.fill(search_sel, nome_questao)
            self.page.click(btn_sel)
            self.page.wait_for_timeout(1500)
        
        # Busca nos resultados da filtragem
        # Moodle 4+ usa varias estruturas, tentamos tudo:
        # 1. Tabela clássica: tr com classes r0/r1
        # 2. Moodle 4+: tbody tr generico ou data-region
        row_selectors = [
            self.selectors["question_bank"]["question_row"],
            "table tbody tr",
            "[data-region='question']",
        ]
      
        for row_sel in row_selectors:
            rows = self.page.locator(row_sel).all()
            if not rows:
                continue
            for row in rows:
                text = row.inner_text()
                if nome_questao.lower() in text.lower():
                    # Moodle 4+: O link da prévia fica ESCONDIDO dentro do dropdown "Editar"
                    # Estrategia: pegar qualquer <a> com href contendo preview.php na linha inteira
                    preview_link = row.locator("a[href*='preview.php']").first
                    if preview_link.count() > 0:
                        return preview_link
                    
                    # Fallback: seletor do config  
                    icon_sel = self.selectors["question_bank"]["preview_action_icon"]
                    preview_btn = row.locator(icon_sel).first
                    if preview_btn.count() > 0:
                        return preview_btn
                        
        logger.warning(f"Questão '{nome_questao}' não localizada nas linhas do banco de questões.")
        return None

    def interagir_alternativa_texto(self, texto_buscado: str, page_alvo: Page = None) -> bool:
        """Procura o texto na lista de alternativas exibida e clica no radio."""
        pg = page_alvo or self.page
        from .text_normalizer import normalize_text
        buscado = normalize_text(texto_buscado)
        
        # Estrategia 1: Buscar por labels dentro de .answer
        opcoes = pg.locator(".answer label, .answeroptions label, .formulation label").all()
        
        for op in opcoes:
            if buscado in normalize_text(op.inner_text()):
                op.click()
                return True
        
        # Estrategia 2: Buscar inputs radio/checkbox e seus pais
        radios = pg.locator("input[type='radio'], input[type='checkbox']").all()
        for radio in radios:
            parent = radio.locator("..")  # pai direto
            if buscado in normalize_text(parent.inner_text()):
                parent.click()
                return True
                
        return False

    def submeter_resposta(self, page_alvo: Page = None):
        pg = page_alvo or self.page
        # Tentar varios botoes de submit comuns do Moodle
        submit_selectors = [
            self.selectors["preview_window"]["submit_button"],
            "input[value='Enviar e finalizar']",
            "input[value='Submit and finish']",
            "button:has-text('Enviar')",
        ]
        for sel in submit_selectors:
            if pg.locator(sel).count() > 0:
                pg.locator(sel).first.click()
                pg.wait_for_timeout(1000)
                return

    def reiniciar_tentativa(self, page_alvo: Page = None):
        pg = page_alvo or self.page
        restart_selectors = [
            self.selectors["preview_window"]["start_again_button"],
            "input[value='Começar de novo']",
            "input[value='Start again']",
            "button:has-text('Começar de novo')",
        ]
        for sel in restart_selectors:
            if pg.locator(sel).count() > 0:
                pg.locator(sel).first.click()
                pg.wait_for_timeout(800)
                return
