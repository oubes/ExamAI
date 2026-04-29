from pathlib import Path
import yaml
import inspect

def load_config(file_name="config.yaml"):
    caller_frame = inspect.stack()[1]
    caller_filename = caller_frame.filename
    
    base_path = Path(caller_filename).parent
    
    file_path = base_path / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found at: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)