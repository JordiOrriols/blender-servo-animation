import importlib
import sys
from pathlib import Path


root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

addon = importlib.import_module("addon")
addon.register()
