import sys
from pathlib import Path
from dotenv import load_dotenv

# Adiciona o diretório raiz ao PYTHONPATH para imports funcionarem
sys.path.append(str(Path(__file__).parent))

from src.orchestrator import Orchestrator

def main():
    print("Iniciando Moodle Question Checker...")
    load_dotenv()
    
    print("\n==================================")
    course_id = input("[?] Digite o ID numérico do curso (ex: 53): ").strip()
    if not course_id.isdigit():
        print("⚠️ ID inválido! Insira apenas números (ex: 53).")
        sys.exit(1)
    print("==================================\n")
    
    orchestrator = Orchestrator(course_id=course_id)
    try:
        orchestrator.run()
    except Exception as e:
        print(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
