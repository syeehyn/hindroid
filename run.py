import sys
import json
import os
from src.utils import get_data
from src.feature import get_apps_info
from glob import glob
def main(targets):
    if 'data' in targets:
        cfg = json.load(open('./config/data-params.json'))
        get_data(**cfg)
    if 'process' in targets:
        cfg = json.load(open('./config/features.json'))
        get_apps_info(**cfg)
    if 'data-test' in targets:
        cfg = json.load(open('./config/test-params.json'))
        get_data(**cfg)
    return

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)