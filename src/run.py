import sys
import json
import os
from utils import get_data
from feature import get_apps_info
def main(targets):
    if 'data' in targets:
        cfg = json.load(open('../config/random_sampling_urls.json'))
        get_data(**cfg)
    if 'process' in targets:
        cfg = json.load(open('../config/features.json'))
        get_apps_info(**cfg)
    if 'data-test' in targets:
        cfg = json.load(open('../config/testdata.json'))
        get_data(**cfg)
    if "process-test" in targets:
        cfg = json.load(open('../config/testfeatures.json'))
        get_apps_info(**cfg)
    return

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)