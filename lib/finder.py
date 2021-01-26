import importlib
from pathlib import Path

# Initialize all flows
paths = Path("flows").glob("**/*.py")
for path in paths:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

from .flow import flows
