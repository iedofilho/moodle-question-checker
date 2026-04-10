from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Alternativa:
    chave: str
    texto: str

@dataclass
class Questao:
    id: str
    nome: str
    tipo: str
    enunciado: str
    alternativas: List[Alternativa]
    resposta_correta: List[str]

    @classmethod
    def do_dict(cls, data: dict):
        alternativas = [Alternativa(**alt) for alt in data.get('alternativas', [])]
        return cls(
            id=data['id'],
            nome=data['nome'],
            tipo=data['tipo'],
            enunciado=data['enunciado'],
            alternativas=alternativas,
            resposta_correta=data['resposta_correta']
        )

@dataclass
class ResultadoValidacao:
    questao_id: str
    questao_nome: str
    tipo: str
    status_estrutura: str = "PENDENTE"
    status_funcional: str = "PENDENTE"
    divergencias: List[str] = field(default_factory=list)
    erro_execucao: str = ""
    screenshot_inicial: str = ""
    screenshot_correta: str = ""
    screenshot_errada: str = ""
    
    def adicionar_divergencia(self, diver: str):
        self.divergencias.append(diver)
