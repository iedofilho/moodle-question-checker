from playwright.sync_api import sync_playwright, Browser, Page, Playwright, Route
from .logger_config import get_logger
from .config_loader import get_env_vars, get_selectors

logger = get_logger(__name__)

class MoodleClient:
    def __init__(self):
        self.playwright: Playwright = sync_playwright().start()
        self.envs = get_env_vars()
        self.selectors = get_selectors()
        
        args = []
        # O modo visual está fixado pois necessitamos interação humana inicial
        self.browser: Browser = self.playwright.chromium.launch(
            headless=self.envs["headless"],
            slow_mo=self.envs["slow_mo"],
            args=args
        )
        self.context = self.browser.new_context(viewport={"width": 1280, "height": 800})
        
        # 🛡️ GUARDRAIL PRINCIPAL: INSERE FILTRO EM TODAS AS REQUESTS
        self.context.route("**/*", self._guardrail_read_only)
        
        self.page: Page = self.context.new_page()

    def _guardrail_read_only(self, route: Route):
        """
        Bloqueia todas as requisições que modificam estado no Moodle,
        exceto o login e a página de prévia.
        """
        request = route.request
        method = request.method.upper()
        url = request.url.lower()

        # Deixa passar requisições normais de leitura de página (GET, HEAD, CSS, JS)
        if method in ["GET", "HEAD", "OPTIONS"]:
            return route.continue_()

        # O POST é usado para envio de formulários e edições
        if method == "POST":
            # 1. Permite os envios do formulário de Login do usuário
            if "login/index.php" in url or "login" in url:
                return route.continue_()
            
            # 2. Permite interações dentro do Popup de Visualização da questão (TENTATIVAS)
            if "question/preview.php" in url:
                return route.continue_()
                
            # 3. Permite os AJAX Inofensivos do Moodle (que buscam blocos, recentes, etc) pra não quebrar a UI
            if "lib/ajax/service.php" in url:
                return route.continue_()
                
            # 4. Evita bloquear silenciosamente extensões de segurança do usuário (Kaspersky)
            if "kaspersky-labs.com" in url:
                return route.continue_()

        # BLOQUEIA ESTUDOS, DELETES, SALVAMENTOS NO BANCO ETC
        logger.warning(f"🛡️ GUARDRAIL ATIVADO: Bloqueou alteração externa forçada ({method} {url})")
        route.abort()

    def do_login(self, timeout_ms=300000):
        """Navega até o Moodle e espera o usuário fazer o login humanamente."""
        from urllib.parse import urljoin
        login_url = urljoin(self.envs['url'], "/login/?lang=pt_br")
        logger.info(f"Navegando para o login: {login_url}...")
        self.page.goto(login_url, wait_until="commit")

        logger.info("⏸️ AUTOMAÇÃO ESTÁ PAUSADA!")
        logger.info("Por favor, localize rapidamente a janela recém aberta e efetue seu login manualmente.")
        logger.info(f"O robô ficará monitorando por até {int(timeout_ms/1000/60)} minutos a sua transição...")
        
        # Aguarda algum elemento estrutural forte confirmando dashboard logado.
        # Em Moodle com temas customizados das Faculdades, buscar o link de "Sair" (logout.php) 
        # ou a página de dashboard (#page-my-index) resolve 100% dos travamentos de seletor customizado.
        try:
            self.page.wait_for_selector(".usermenu, .userbutton, #user-menu-toggle, .userpicture, a[href*='logout.php'], body#page-my-index", timeout=timeout_ms)
            logger.info("✅ Login Humano Identificado! Devolvendo o controle ao Robô e inicializando o scan...")
            self.page.wait_for_timeout(2000) # delay para Moodle descarregar transição do login
        except Exception as e:
            logger.error("❌ O fluxo falhou pois expirou o tempo de espera para login humano.")
            self.close()
            raise e

    def close(self):
        try:
            self.context.close()
            self.browser.close()
            self.playwright.stop()
        except Exception:
            pass
