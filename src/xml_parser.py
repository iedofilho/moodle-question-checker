import xml.etree.ElementTree as ET
from pathlib import Path
import string
from .models import Questao, Alternativa

def parse_moodle_xml(file_path: Path) -> list:
    """Consome o XML gerado pra importação e converte para nossa classe Questao"""
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo XML não encontrado: {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    start = content.find("<?xml")
    end = content.rfind("</quiz>")
    if start != -1 and end != -1:
        # Fatiamento cirúrgico para evitar o lixo (relatórios de texto) depois do XML
        content = content[start:end+7]
        
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        raise ValueError(f"XML corrompido ou mal formado: {e}")
        
    questoes = []
    seq_id = 1
    
    for q in root.findall("question"):
        q_type = q.get("type")
        if q_type not in ["multichoice", "essay"]:
            continue
            
        name_node = q.find("./name/text")
        nome = name_node.text if name_node is not None else f"Questão {seq_id}"
        
        qtext_node = q.find("./questiontext/text")
        enunciado = qtext_node.text if qtext_node is not None else ""
        
        if q_type == "multichoice":
            alternativas = []
            respostas_corretas = []
            answers = q.findall("answer")
            
            for idx, ans in enumerate(answers):
                fraction = ans.get("fraction", "0")
                ans_text_node = ans.find("text")
                texto_alt = ans_text_node.text if (ans_text_node is not None and ans_text_node.text) else ""
                
                # Gera uma letra mockada (a, b, c) de acordo com o index da tag
                chave = string.ascii_lowercase[idx] if idx < 26 else str(idx)
                alternativas.append(Alternativa(chave=chave, texto=texto_alt))
                
                if fraction == "100":
                    respostas_corretas.append(chave)
                    
            questoes.append(Questao(
                id=f"q_{seq_id}",
                nome=nome.strip(),
                tipo="multipla_escolha",
                enunciado=enunciado,
                alternativas=alternativas,
                resposta_correta=respostas_corretas
            ))
            
        elif q_type == "essay":
            questoes.append(Questao(
                id=f"q_{seq_id}",
                nome=nome.strip(),
                tipo="aberta",
                enunciado=enunciado,
                alternativas=[],
                resposta_correta=[]
            ))
            
        seq_id += 1
        
    return questoes
