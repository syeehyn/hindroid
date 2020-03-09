import sys
import json
import os
from src.datasets import *
from src.utils import create_metadata
from src.features import extract_benign
from glob import glob
def main(targets):
    if 'metadata' in targets:
        create_metadata()
    if 'sampling' in targets:
        cfg = json.load(open('./config/sample-params.json'))
        sampling(**cfg)
    if 'sampling-test' in targets:
        cfg = cfg = json.load(open('./config/test-sample.json'))
        sampling(**cfg)
    if 'data' in targets:
        cfg = json.load(open('./config/data-params.json'))
        get_data(**cfg)
    if 'process' in targets:
        extract_benign()
    if 'process-test' in targets:
        extract_benign(True)
    if 'data-test' in targets:
        cfg = json.load(open('./config/test-params.json'))
        get_data(**cfg)
    return

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)