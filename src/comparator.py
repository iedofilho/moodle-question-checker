from typing import List
from .models import Questao, ResultadoValidacao
from .text_normalizer import normalize_text

class Comparator:
    def compare_estrutura(self, q_json: Questao, texto_enunciado: str, alts_moodle: list, result: ResultadoValidacao):
        """Compara a questão fonte vs a carregada em text da tela do moodle"""
        
        # 1. Enunciado (comparaçao flexível)
        norm_json_enunc = normalize_text(q_json.enunciado)
        norm_moodle_enunc = normalize_text(texto_enunciado)
        
        # Permite match parcial do texto do word no moodle.
        if norm_json_enunc not in norm_moodle_enunc:
            result.adicionar_divergencia(f"Enunciado destoa: Esperado conter '{norm_json_enunc[:30]}...'")

        # 2. Alternativas
        moodle_alts_norms = [normalize_text(a["texto_moodle"]) for a in alts_moodle]
        
        for alt_json in q_json.alternativas:
            norm_json_alt = normalize_text(alt_json.texto)
            achou = any(norm_json_alt in malt for malt in moodle_alts_norms)
            if not achou:
                result.adicionar_divergencia(f"Alternativa não encontrada no Moodle: '{norm_json_alt}'")
        
        if len(result.divergencias) == 0:
            result.status_estrutura = "OK"
        else:
            result.status_estrutura = "FALHOU"
