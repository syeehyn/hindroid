import pandas as pd
import os
import json
from glob import glob
from tqdm import tqdm
from ._extraction import _get_app_info
from pathlib import Path
import dask
from dask.distributed import Client
from dask import delayed
import psutil
import logging
logger = logging.getLogger("distributed.utils_perf")
logger.setLevel(logging.ERROR)
NUM_WORKER = psutil.cpu_count(logical = False)
ROOT_DIR = Path(__file__).parent.parent.parent
def extract_benign(test = False):
    """[extract basic features of benign apps]
    Arguments:
        test {[boolean]} -- [to extract feature from test set or not]
    """
    if not test:
        fp = os.path.join(ROOT_DIR, 'data/datasets/raw/smali')
        op = os.path.join(ROOT_DIR, 'data/datasets/interim/features')
    else:
        fp = os.path.join(ROOT_DIR, 'data/tests/raw/smali')
        op = os.path.join(ROOT_DIR, 'data/tests/interim/features')
    if not os.path.exists(op):
        if not test:
            try:
                os.mkdir(os.path.join(ROOT_DIR, 'data/tests/interim'))
            except FileExistsError:
                pass
        else:
            try:
                os.mkdir(os.path.join(ROOT_DIR, 'data/tests/interim'))
            except FileExistsError:
                pass
        os.mkdir(op)
    op_csv = [i.split('/')[-1][:-4] for i in glob(op + '/*.csv')]
    applist = [i.split('/')[-1] for i in glob(fp + '/*')]
    client = Client(n_workers = NUM_WORKER)
    # print("Dashboard Address: " + 'http://127.0.0.1:' + str(client.scheduler_info()['services']['dashboard'])+'/status')
    jobs = [delayed(_get_app_info)(fp, app) for app in applist if app not in op_csv]
    for i in tqdm(range(0, len(jobs), NUM_WORKER)):
        proc_jobs = jobs[i: i+NUM_WORKER]
        dfs = dask.compute(proc_jobs)[0]
        for j in range(len(dfs)):
            dfs[j]['malware'] = 0
            dfs[j].to_csv(os.path.join(op, applist[i + j] + '.csv'), index = False)
    print('all benign apps (total {}) extracted'.format(len(applist)))
    return

def extract_malware(fp, test = False):
    """[extract basic features of malware apps]
    Arguments:
        fp {[string]} -- [file path of malware apps]
        test {[boolean]} -- [to extract feature from test set or not]
    """
    if not test:
        op = os.path.join(ROOT_DIR, 'data/datasets/interim/features')
    else:
        op = os.path.join(ROOT_DIR, 'data/tests/interim/features')
    if not os.path.exists(op):
        os.mkdir(op)
    op_csv = [i.split('/')[-1][:-4] for i in glob(op + '/*.csv')]
    applist = [i.split('/')[-1] for i in glob(fp + '/*')]
    client = Client(n_workers = NUM_WORKER)
    for app in tqdm(applist):
        if app not in op_csv:
            df = _get_app_info(fp, app)
            if len(df) != 0:
                df['app'] = app
                df['malware'] = 1
                df.to_csv(os.path.join(op, app + '.csv'), index = False)
    print("all malware apps (total {}) extracted".format(len(applist)))
    return