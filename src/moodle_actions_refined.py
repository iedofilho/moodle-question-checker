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

    def _wait_question_bank_ready(self) -> None:
        """Espera somente o necessario para a tela do banco ficar util."""
        self.page.wait_for_load_state("domcontentloaded")
        self.page.locator("body#page-question-edit").first.wait_for(state="visible", timeout=10000)
        self.page.locator("#categoryquestions tbody tr").first.wait_for(state="visible", timeout=10000)

    def _wait_preview_ready(self, page_alvo: Page = None) -> None:
        """Espera leve para preview.php, sem depender de load/networkidle."""
        pg = page_alvo or self.page
        pg.wait_for_load_state("domcontentloaded")

        for seletor in [".qtext", ".answer", "input[name='finish']", "input[name='restart']"]:
            try:
                pg.locator(seletor).first.wait_for(state="visible", timeout=4000)
                return
            except Exception:
                continue

    def _get_preview_href_from_row(self, row) -> Optional[str]:
        preview = row.locator("a[href*='previewquestion/preview.php'], a[href*='preview.php']")
        if preview.count() == 0:
            return None
        return preview.first.get_attribute("href")

    def buscar_questao(
        self,
        nome_questao: str,
        search_variants: List[str] = None,
        course_id: str = None,
        context_url: str = None,
    ) -> Optional[str]:
        route = f"/question/edit.php?courseid={course_id}" if course_id else "/question/edit.php"
        q_url = context_url or urljoin(self.envs["url"], route)

        if self._current_bank_url != q_url:
            self.page.goto(q_url)
            self._current_bank_url = q_url
            self._wait_question_bank_ready()

            show_all = self.page.locator("button[data-filteraction='showall']")
            if show_all.count() > 0:
                try:
                    show_all.first.click()
                    self.page.locator("#categoryquestions tbody tr").last.wait_for(state="attached", timeout=10000)
                except Exception:
                    pass

        variants = search_variants or [nome_questao]
        editables = self.page.locator(
            "#categoryquestions span.inplaceeditable[data-component='qbank_viewquestionname'][data-itemtype='questionname']"
        )

        for variant in variants:
            escaped_variant = variant.replace("\\", "\\\\").replace('"', '\\"')
            selector = (
                "#categoryquestions "
                f"span.inplaceeditable[data-component='qbank_viewquestionname'][data-itemtype='questionname'][data-value=\"{escaped_variant}\"]"
            )
            match = self.page.locator(selector)
            if match.count() > 0:
                logger.info(f"  -> Encontrada via data-value: '{variant}'")
                href = self._get_preview_href_from_row(match.first.locator("xpath=ancestor::tr"))
                if href:
                    return href

        logger.info("  -> Tentando busca por texto parcial...")
        for editable in editables.all():
            dv = editable.get_attribute("data-value") or ""
            for variant in variants:
                if variant.lower() in dv.lower() or dv.lower() in variant.lower():
                    logger.info(f"  -> Match parcial: '{dv}' ~ '{variant}'")
                    href = self._get_preview_href_from_row(editable.locator("xpath=ancestor::tr"))
                    if href:
                        return href

        for row in self.page.locator("#categoryquestions tbody tr").all():
            try:
                text = row.inner_text()
            except Exception:
                continue

            for variant in variants:
                if variant.lower() in text.lower():
                    href = self._get_preview_href_from_row(row)
                    if href:
                        logger.info(f"  -> Match por inner_text: '{variant}'")
                        return href

        logger.warning(f"Questao '{nome_questao}' nao localizada no banco de questoes.")
        return None

    def interagir_alternativa_texto(self, texto_buscado: str, page_alvo: Page = None) -> bool:
        pg = page_alvo or self.page
        from .text_normalizer import normalize_text

        self._wait_preview_ready(pg)
        buscado = normalize_text(texto_buscado)

        for row in pg.locator(".answer .r0, .answer .r1").all():
            text_el = row.locator("[data-region='answer-label'] .flex-fill, .flex-fill")
            if text_el.count() == 0:
                continue

            texto_alt = normalize_text(text_el.first.inner_text())
            if buscado in texto_alt or texto_alt in buscado:
                input_resposta = row.locator("input[type='radio'], input[type='checkbox']")
                if input_resposta.count() > 0:
                    input_resposta.first.click()
                    return True
        return False

    def submeter_resposta(self, page_alvo: Page = None):
        pg = page_alvo or self.page
        self._wait_preview_ready(pg)
        btn = pg.locator("input[name='finish']")
        if btn.count() > 0:
            btn.first.click()
            pg.wait_for_timeout(1500)

    def reiniciar_tentativa(self, page_alvo: Page = None):
        pg = page_alvo or self.page
        self._wait_preview_ready(pg)
        btn = pg.locator("input[name='restart']")
        if btn.count() > 0:
            btn.first.click()
            pg.wait_for_timeout(1000)
