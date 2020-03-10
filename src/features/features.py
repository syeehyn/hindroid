import pandas as pd
import os
import json
from glob import glob
from tqdm import tqdm
from ._extraction import _get_app_info
from pathlib import Path
import dask
from dask.distributed import Client, progress
# from dask.diagnostics import ProgressBar
from dask import delayed
import psutil
import logging
logger = logging.getLogger("distributed.utils_perf")
logger.setLevel(logging.ERROR)
NUM_WORKER = psutil.cpu_count(logical = False)
ROOT_DIR = Path(__file__).parent.parent.parent

def _signout(clt):
    clt.close()
    return
def extract_benign(test = False):
    """[extract basic features of benign apps]
    Arguments:
        test {[boolean]} -- [to extract feature from test set or not]
    """
    if not test:
        fp = os.path.join(ROOT_DIR, 'data/datasets/raw/smali')
        op = os.path.join(ROOT_DIR, 'data/datasets/interim/b_features')
    else:
        fp = os.path.join(ROOT_DIR, 'data/tests/raw/smali')
        op = os.path.join(ROOT_DIR, 'data/tests/interim/b_features')
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
    jobs = [delayed(_get_app_info)(fp, app, 0, op) for app in applist if app not in op_csv]
    task = dask.persist(jobs)
    print('total {} benign apps to be extracted'.format(len(applist)))
    progress(task)
    print("\n Extracted")
    return _signout(client)
def extract_malware(fp, test = False):
    """[extract basic features of malware apps]
    Arguments:
        fp {[string]} -- [file path of malware apps]
        test {[boolean]} -- [to extract feature from test set or not]
    """
    if not test:
        op = os.path.join(ROOT_DIR, 'data/datasets/interim/m_features')
    else:
        op = os.path.join(ROOT_DIR, 'data/tests/interim/m_features')
    if not os.path.exists(op):
        os.mkdir(op)
    op_csv = [i.split('/')[-1][:-4] for i in glob(op + '/*.csv')]
    applist = [i.split('/')[-1] for i in fp]
    client = Client(n_workers = NUM_WORKER)
    jobs = [delayed(_get_app_info)(fp, app, 1, op) for app in applist if app not in op_csv]
    task = dask.persist(jobs)
    print("total {} malware apps to be extracted".format(len(applist)))
    progress(task)
    print("\n Extracted")
    return _signout(client)