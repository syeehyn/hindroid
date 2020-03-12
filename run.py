import sys
import json
import os
from src.datasets import *
from src.utils import create_metadata
from src.features import extract_benign, extract_malware
from src.models import construct_matrices
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
    if 'data-test' in targets:
        cfg = json.load(open('./config/test-params.json'))
        get_data(**cfg)
    if 'process' in targets:
        fp = json.load(open('./config/data-params.json'))['m_dir']
        extract_benign()
        extract_malware(fp)
    if 'process-test' in targets:
        fp = json.load(open('./config/test-params.json'))['m_dir']
        extract_benign(True)
        extract_malware(fp, True)
    if 'matrix' in targets:
        construct_matrices(False, False, False, True)
    if 'matrix-test' in targets:
        construct_matrices(True, True, True, True)
    return

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)