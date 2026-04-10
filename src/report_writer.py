import pandas as pd
from pathlib import Path
from typing import List
from .models import ResultadoValidacao
from .utils import get_project_root

class ReportWriter:
    def __init__(self, output_dir: str):
        self.out_path = get_project_root() / output_dir
        self.out_path.mkdir(parents=True, exist_ok=True)
        
    def generate(self, resultados: List[ResultadoValidacao]):
        data = []
        for r in resultados:
            row = {
                "id": r.questao_id,
                "nome": r.questao_nome,
                "tipo": r.tipo,
                "status_estrutura": r.status_estrutura,
                "status_funcional": r.status_funcional,
                "divergencias": "\n".join(r.divergencias),
                "erro_execucao": r.erro_execucao,
                "screenshot_inicial": r.screenshot_inicial,
                "screenshot_correta": r.screenshot_correta,
                "screenshot_errada": r.screenshot_errada
            }
            data.append(row)
            
        df = pd.DataFrame(data)
        csv_m = self.out_path / "relatorio_validacao.csv"
        xlsx_m = self.out_path / "relatorio_validacao.xlsx"
        
        df.to_csv(csv_m, index=False, encoding='utf-8')
        df.to_excel(xlsx_m, index=False)
        print(f"Relatório gerado em: {xlsx_m}")
