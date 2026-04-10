import json
from pathlib import Path
from jsonschema import validate, ValidationError

def validar_questoes_json(file_path: Path):
    base_dir = Path(__file__).parent.parent
    schema_path = base_dir / "schema" / "questoes.schema.json"
    
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
        
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo JSON de entrada nao encontrado em {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    try:
        validate(instance=data, schema=schema)
        return True, data
    except ValidationError as e:
        return False, str(e)
