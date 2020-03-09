import sys
sys.path.append('../src')
from src.utils import _get_malware_dir
import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent.parent
META_DIR = os.path.join(ROOT_DIR, 'data/metadata/metadata.csv')
APP_DIR = os.path.join(ROOT_DIR, 'data/datasets/')
TEST_DIR = os.path.join(ROOT_DIR, 'data/tests/')
def sampling(**cfg):
    size, test, mfp = cfg['size'], cfg['test'], cfg['mfp']
    if not test:
        fp = APP_DIR
        op = os.path.join(ROOT_DIR, 'config/data-params.json')
    else:
        fp = TEST_DIR
        op = os.path.join(ROOT_DIR, 'config/test-params.json')
    metadata = pd.read_csv(META_DIR)
    malware_dir = _get_malware_dir(mfp)
    urls = metadata.sample(size)['loc'].tolist()
    malwares = np.random.choice(malware_dir, size//2).tolist()
    app_url = {
        'dir': fp,
        'm_dir': malwares,
        'urls': urls,
        'verbose': False,
        'clean': True
    }
    with open(op, 'w') as f:
        json.dump(app_url, f)