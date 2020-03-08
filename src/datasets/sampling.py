import pandas as pd
import json
import os
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent.parent
META_DIR = os.path.join(ROOT_DIR, 'data/metadata/metadata.csv')
APP_DIR = os.path.join(ROOT_DIR, 'data/datasets/')
TEST_DIR = os.path.join(ROOT_DIR, 'data/tests/')
def sampling(**cfg):
    mode, size, test = cfg['mode'], cfg['size'], cfg['test']
    if not test:
        fp = APP_DIR
        op = os.path.join(ROOT_DIR, 'config/data-params.json')
    else:
        fp = TEST_DIR
        op = os.path.join(ROOT_DIR, 'config/test-params.json')
    metadata = pd.read_csv(META_DIR)
    if mode == 'random':
        urls = metadata.sample(size)['loc'].tolist()
        app_url = {
            'dir': fp,
            'urls': urls,
            'verbose': False,
            'clean': True
        }
    with open(op, 'w') as f:
        json.dump(app_url, f)