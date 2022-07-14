import json
from pathlib import Path
from typing import Dict


def load_json_test(data_filename: str) -> Dict:
    """Load a file containing a json patch object, possibly with variable substitutions required."""
    input_json_file = Path("data") / data_filename
    data: Dict = json.loads(input_json_file.read_text())
    return data
