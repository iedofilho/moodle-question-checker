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
        
        input_files = list(input_dir.glob("*.json")) + list(input_dir.glob("*.xml"))
        
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
                questoes = [Questao.do_dict(q) for q in msg_ou_dados]
                
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
                logger.info(f"-- Processando [{q.id}] {q.nome} --")
                try:
                    # 1. Busca a questao passando o ID do curso
                    btn_prev = actions.buscar_questao(q.nome, course_id=self.course_id)
                    if not btn_prev:
                        res.erro_execucao = "Botao preview (lupa) nao encontrado no Banco de Questoes. Cheque search_name."
                        res.status_estrutura = "FALHOU"
                        logger.warning(res.erro_execucao)
                        resultados.append(res)
                        continue
                        
                    # Moodle costuma abrir pop-up pra preview. Precisamos esperar o novo popup.
                    with client.context.expect_page() as novo_contexto:
                        btn_prev.click()
                        
                    pg_preview = novo_contexto.value
                    pg_preview.wait_for_load_state("networkidle")
                    
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
                        logger.info(" -> Questão Aberta Identificada. Pulando o clique de respostas.")
                        res.status_funcional = "IGNORADO"
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
                        
                        if not check_feedback_ok(pg_preview):
                            res.adicionar_divergencia("Feedback Visual não retornou classe de 'Acerto' no Moodle.")
                            res.status_funcional = "FALHOU"

                        actions.reiniciar_tentativa(pg_preview)
                    
                    # Achar alternativa errada para teste Incorreto
                    errs = [a.texto for a in q.alternativas if a.chave not in q.resposta_correta]
                    if errs:
                        err_text = errs[0]
                        actions.interagir_alternativa_texto(err_text, pg_preview)
                        actions.submeter_resposta(pg_preview)
                        res.screenshot_errada = self.ss_manager.take(pg_preview, f"{q.id}_03_err")
                        
                        if not check_feedback_erro(pg_preview):
                            res.adicionar_divergencia("Feedback Visual não retornou classe de 'Erro' no Moodle.")
                            res.status_funcional = "FALHOU"
                            
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
