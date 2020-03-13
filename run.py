import sys
import json
import os
from src.datasets import *
from src.utils import create_metadata
from src.features import extract_benign, extract_malware
from src.models import construct_matrices, evaluate, baseline
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
        construct_matrices(False, True, True, True)
    if 'matrix-test' in targets:
        construct_matrices(True, True, True, True)
    if 'baseline' in targets:
        return baseline.evaluate(False)
    if 'baseline-test' in targets:
        return baseline.evaluate(True)
    if 'evaluate' in targets:
        import pandas as pd
        result = evaluate(False)
        print('training metrics: ')
        print(result[0])
        print('testing metrics: ')
        print(result[1])
        try:
            os.mkdir('./data/datasets/processed/results')
        except:
            pass
        result[0].to_csv('./data/datasets/processed/results/training.csv', index = False)
        result[1].to_csv('./data/datasets/processed/results/testing.csv', index = False)
    if 'evaluate-test' in targets:
        import pandas as pd
        result = evaluate(True)
        print('training metrics: ')
        print(result[0])
        print('testing metrics: ')
        print(result[1])
        try:
            os.mkdir('./data/tests/processed/results')
        except:
            pass
        result[0].to_csv('./data/tests/processed/results/training.csv', index = False)
        result[1].to_csv('./data/tests/processed/results/testing.csv', index = False)
    if 'project' in targets:
        cfg = json.load(open('./config/data-params.json'))
        get_data(**cfg)
        fp = json.load(open('./config/data-params.json'))['m_dir']
        extract_benign(False)
        extract_malware(fp, False)
        construct_matrices(False, True, True, True)
        result = evaluate(False)
        try:
            os.mkdir('./data/datasets/processed/results')
        except:
            pass
        result[0].to_csv('./data/datasets/processed/results/training.csv', index = False)
        result[1].to_csv('./data/datasets/processed/results/testing.csv', index = False)
    if 'test-project' in targets:
        cfg = json.load(open('./config/test-params.json'))
        get_data(**cfg)
        fp = json.load(open('./config/test-params.json'))['m_dir']
        extract_benign(True)
        extract_malware(fp, True)
        construct_matrices(True, True, True, True)
        result = evaluate(True)
        try:
            os.mkdir('./data/tests/processed/results')
        except:
            pass
        result[0].to_csv('./data/tests/processed/results/training.csv', index = False)
        result[1].to_csv('./data/tests/processed/results/testing.csv', index = False)
    return

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)