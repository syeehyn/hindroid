import sys
sys.path.append('../src')
from src.utils import _get_malware_dir
import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
from src import *
META_DIR = os.path.join(ROOT_DIR, 'data/metadata/metadata.csv')
def sampling(**cfg):
    size, test, mfp = cfg['size'], cfg['test'], cfg['mfp']
    if not test:
        fp = 'data/datasets/'
        op = os.path.join(ROOT_DIR, 'config/data-params.json')
    else:
        fp = 'data/tests/'
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