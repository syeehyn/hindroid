import sys
import json
import os
from src.datasets import get_data
from src.features import extract_benign
from glob import glob
def main(targets):
    if 'data' in targets:
        cfg = json.load(open('./config/data-params.json'))
        get_data(**cfg)
    if 'process' in targets:
        extract_benign()
    if 'data-test' in targets:
        cfg = json.load(open('./config/test-params.json'))
        get_data(**cfg)
    if 'process-test' in targets:
        extract_benign(True)
    return

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)