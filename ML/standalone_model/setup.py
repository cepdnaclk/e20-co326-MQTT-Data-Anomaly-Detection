import sys
from pathlib import Path

# Add project root to path for easy imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# Standard paths
MODEL_DIR = Path(__file__).resolve().parent
DATA_DIR = MODEL_DIR.parent
DATA_PATH = DATA_DIR / "embedded_system_network_security_dataset.csv"
