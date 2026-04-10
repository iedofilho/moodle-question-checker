from pathlib import Path
from playwright.sync_api import Page
from .utils import get_project_root

class ScreenshotManager:
    def __init__(self, output_dir: str):
        self.out_path = get_project_root() / output_dir
        self.out_path.mkdir(parents=True, exist_ok=True)
    
    def take(self, page: Page, name: str) -> str:
        safe_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c=='_']).rstrip()
        filename = f"{safe_name}.png"
        filepath = self.out_path / filename
        page.screenshot(path=str(filepath), full_page=True)
        return str(filepath.absolute())
