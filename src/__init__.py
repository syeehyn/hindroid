from pathlib import Path
import psutil
ROOT_DIR = Path(__file__).parent.parent
NUM_WORKER = psutil.cpu_count(logical = False)