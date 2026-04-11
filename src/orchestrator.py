import json
from pathlib import Path
from .utils import setup_directories, get_project_root
from .config_loader import get_settings
from .logger_config import get_logger
from .schema_validator import validar_questoes_json
from .models import Questao, ResultadoValidacao
from .moodle_client import MoodleClient
from .moodle_actions import MoodleActions
from .moodle_extractors import extract_texto_enunciado, extract_alternativas, check_feedback_ok, check_feedback_erro
from .comparator import Comparator
from .screenshot_manager import ScreenshotManager
from .report_writer import ReportWriter

logger = get_logger(__name__)

class Orchestrator:
    def __init__(self, course_id: str):
        self.course_id = course_id
        self.settings = get_settings()
        setup_directories(self.settings)
        self.ss_manager = ScreenshotManager(self.settings["directories"]["screenshots"])
        self.report_writer = ReportWriter(self.settings["directories"]["output"])
        logger.info("Orquestrador inicializado.")
        
    def run(self):
        # 1. Carregar Arquivo de Entrada
        base_dir = get_project_root()
        input_dir = base_dir / self.settings["directories"]["input"]
        
        input_files = list(input_dir.glob("*.xml")) + list(input_dir.glob("*.json"))
        
        if not input_files:
            logger.error("Nenhum arquivo .json nem .xml encontrado na pasta input/")
            return
            
        input_file = input_files[0]
        extensao = input_file.suffix.lower()
        logger.info(f"Identificado arquivo de base {extensao.upper()}: ({input_file.name})")
        
        questoes = []
        try:
            if extensao == ".xml":
                from .xml_parser import parse_moodle_xml
                questoes = parse_moodle_xml(input_file)
            elif extensao == ".json":
                from .schema_validator import validar_questoes_json
                valido, msg_ou_dados = validar_questoes_json(input_file)
                if not valido:
                    logger.error(f"Erro de Schema JSON: {msg_ou_dados}")
                    return
                import re
                for q_dados in msg_ou_dados:
                    q = Questao.do_dict(q_dados)
                    # HARMONIZADOR INTELIGENTE (JSON -> Moodle)
                    # O Moodle da Fundace usa AMBOS os formatos de nome:
                    #   "Fechada 01 - Aula 20"  (questoes mais antigas)
                    #   "Aula 20 - Fechada 01"  (questoes mais recentes)
                    # Aqui geramos todas as variantes para busca flexivel
                    match_aula = re.search(r'(?i)Aula\s*(\d+)', q.nome)
                    match_q = (re.search(r'(?i)(?:quest[aã]o|aberta|fechada|q)\D*(\d+)', q.nome) 
                               or re.search(r'(\d+)\s*$', q.nome))
                    
                    if match_aula and match_q:
                        a_num = str(int(match_aula.group(1))).zfill(2)
                        q_num = str(int(match_q.group(1))).zfill(2)
                        a_raw = str(int(match_aula.group(1)))
                        tipo_label = "Aberta" if q.tipo == "aberta" else "Fechada"
                        
                        # Nome principal (formato mais comum no Moodle)
                        q.nome = f"{tipo_label} {q_num} - Aula {a_num}"
                        # O Moodle da Fundace também pode ter variaveis sem número específico ou formatos mistos
                        q._search_variants = [
                            f"{tipo_label} {q_num} - Aula {a_num}",      # Fechada 01 - Aula 20
                            f"Aula {a_num} - {tipo_label} {q_num}",      # Aula 20 - Fechada 01
                            f"{tipo_label} {q_num} - Aula {a_raw}",      # Fechada 01 - Aula 20 (sem zero)
                            f"Aula {a_raw} - {tipo_label} {q_num}",      # Aula 20 - Fechada 01 (sem zero)
                            f"Aula {a_num} - {tipo_label}",              # Aula 20 - Fechada (sem numero de questao)
                            f"Aula {a_raw} - {tipo_label}",              # Aula 20 - Fechada
                        ]
                    else:
                        q._search_variants = [q.nome]
                            
                    questoes.append(q)
                
            logger.info(f"{len(questoes)} questoes extraidas com sucesso.")
        except Exception as e:
            logger.error(f"Ocorreu um problema interpretando o {extensao.upper()}: {e}")
            return

        # Inicia ambiente Moodle
        client = None
        resultados = []
        
        try:
            client = MoodleClient()
            client.do_login()
            actions = MoodleActions(client.page)
            comparator = Comparator()
            
            for q in questoes:
                res = ResultadoValidacao(questao_id=q.id, questao_nome=q.nome, tipo=q.tipo)
                variants = getattr(q, '_search_variants', [q.nome])
                logger.info(f"-- Processando [{q.id}] {q.nome} --")
                try:
                    # 1. Busca a questao (agora retorna URL string, nao locator)
                    preview_url = actions.buscar_questao(
                        q.nome, 
                        search_variants=variants,
                        course_id=self.course_id
                    )
                    if not preview_url:
                        res.erro_execucao = "Questao nao encontrada no banco. Verifique nome/categoria."
                        res.status_estrutura = "FALHOU"
                        logger.warning(res.erro_execucao)
                        resultados.append(res)
                        continue
                        
                    # Abre aba de preview diretamente via URL
                    pg_preview = client.context.new_page()
                    pg_preview.goto(preview_url)
                    pg_preview.wait_for_load_state("load")
                    
                    # Salva status cru original
                    res.screenshot_inicial = self.ss_manager.take(pg_preview, f"{q.id}_01_init")
                    
                    # 2. Extracao estrutural
                    texto_enunc = extract_texto_enunciado(pg_preview)
                    alts_moodle = extract_alternativas(pg_preview)
                    
                    # 3. Comparacao Estrutural
                    comparator.compare_estrutura(q, texto_enunc, alts_moodle, res)
                    logger.info(f" -> Estrutura: {res.status_estrutura}")
                    
                    if self.settings["behavior"].get("dry_run", False):
                        resultados.append(res)
                        pg_preview.close()
                        continue

                    # 4. Teste Funcional (Acerto e Erro)
                    if q.tipo == "aberta":
                        logger.info(" -> Questao Aberta Identificada. Pulando o clique de respostas.")
                        res.status_funcional = "IGNORADO"
                        res.teste_acerto = "IGNORADO"
                        res.teste_erro = "IGNORADO"
                        pg_preview.close()
                        resultados.append(res)
                        continue
                        
                    res.status_funcional = "OK"
                    
                    # Achar alternativa gabarito pra teste Correto
                    gabs = [a.texto for a in q.alternativas if a.chave in q.resposta_correta]
                    if gabs:
                        gab_text = gabs[0]
                        actions.interagir_alternativa_texto(gab_text, pg_preview)
                        actions.submeter_resposta(pg_preview)
                        res.screenshot_correta = self.ss_manager.take(pg_preview, f"{q.id}_02_corr")
                        
                        if check_feedback_ok(pg_preview):
                            res.teste_acerto = "PASSOU"
                        else:
                            res.teste_acerto = "FALHOU"
                            res.adicionar_divergencia("O sistema não acusou a reposta oficial do JSON como CORRETA na tela.")
                            res.status_funcional = "FALHOU"

                        actions.reiniciar_tentativa(pg_preview)
                    else:
                        res.teste_acerto = "FALHOU"
                        res.adicionar_divergencia("Não achou texto da correta para clicar.")
                    
                    # Achar alternativa errada para teste Incorreto
                    errs = [a.texto for a in q.alternativas if a.chave not in q.resposta_correta]
                    if errs:
                        err_text = errs[0]
                        actions.interagir_alternativa_texto(err_text, pg_preview)
                        actions.submeter_resposta(pg_preview)
                        res.screenshot_errada = self.ss_manager.take(pg_preview, f"{q.id}_03_err")
                        
                        if check_feedback_erro(pg_preview):
                            res.teste_erro = "PASSOU"
                        else:
                            res.teste_erro = "FALHOU"
                            res.adicionar_divergencia("O sistema não acusou a alternativa erronêa como INCORRETA.")
                            res.status_funcional = "FALHOU"
                    else:
                        res.teste_erro = "FALHOU"
                        res.adicionar_divergencia("Não achou errada para testar erro.")
                            
                    pg_preview.close()

                except Exception as e:
                    res.erro_execucao = f"Falha exception: {str(e)}"
                    res.status_estrutura = "FALHOU"
                    logger.error(res.erro_execucao)
                    
                resultados.append(res)
                
            # Gerar relacao final
            self.report_writer.generate(resultados)

        except Exception as global_err:
             logger.error(f"Falha critica no robo: {global_err}")
        finally:
            if client:
                client.close()
            logger.info("Processo concluido!")
