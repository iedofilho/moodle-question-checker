import sys
from pathlib import Path
from dotenv import load_dotenv

# Adiciona o diretório raiz ao PYTHONPATH para imports funcionarem
sys.path.append(str(Path(__file__).parent))

from src.orchestrator import Orchestrator

def main():
    print("Iniciando Moodle Question Checker...")
    load_dotenv()
    
    orchestrator = Orchestrator()
    try:
        orchestrator.run()
    except Exception as e:
        print(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
