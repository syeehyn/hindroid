import sys
sys.path.append('../src')
import os
from dask.distributed import Client, progress
from dask import delayed
import dask
from tqdm import tqdm
from src.utils import _decompose_app
from src.utils import _download_app
import json
import re
from glob import glob
import numpy as np
from pathlib import Path
import psutil
import logging
logger = logging.getLogger("distributed.utils_perf")
logger.setLevel(logging.ERROR)
NUM_WORKER = psutil.cpu_count(logical = False)
ROOT_DIR = Path(__file__).parent.parent.parent
LIMIT = NUM_WORKER * 2
def _signout(clt):
    clt.close()
    return
def _initilize_dataenv(fp):
    filepath = fp
    if not os.path.exists(filepath):
        try:
            os.mkdir(filepath)
        except:
            os.mkdir('data')
            os.mkdir(filepath)
    if not os.path.exists(os.path.join(filepath, 'raw/apps')):
        try:
            os.mkdir(os.path.join(filepath, 'raw'))
            os.mkdir(os.path.join(filepath, 'raw/apps'))
            os.mkdir(os.path.join(filepath, 'raw/smali'))
        except:
            try:
                os.mkdir(os.path.join(filepath, 'raw/apps'))
            except:
                pass
            try: os.mkdir(os.path.join(filepath, 'raw/smali'))
            except:
                pass
def get_data(**cfg):
    """[download and extract the apks]
    Arguments:
        dir {[string]} -- [downloading directory]
        urls {[string]} -- [url link of the file]
        clean {[boolean]} -- [clean apk after decompose or not]
        verbose {[boolean]} -- [verbose the process or not]
    
    Returns:
        [string] -- [success message]
    """
    client = Client(n_workers = NUM_WORKER)
    fp, urls, verbose, clean = cfg['dir'], cfg['urls'], cfg["verbose"], cfg['clean']
    fp = os.path.join(ROOT_DIR, fp)
    _initilize_dataenv(fp)
    def get_app_name(url):
        result = re.findall(r'https:\/\/apkpure.com\/(.*?)\/', url)
        if len(result) != 0:
            return result[0]
        else:
            return None
    downloading = [delayed(_download_app)(url, fp, get_app_name(url)) for url in urls if get_app_name(url) != None]
    task = dask.persist(downloading)
    print('Downloading')
    progress(task)
    print('\n Downloaded')
    extract_app = [i.split('/')[-1] for i in glob(os.path.join(fp, 'raw/apps/*'))]
    extract_app = [delayed(_decompose_app)(fp, app, clean,verbose) for app in extract_app]
    print('Total {} apk will be extracted'.format(len(extract_app)))
    N = int(np.ceil(len(extract_app) / LIMIT))
    for i in range(0, len(extract_app), LIMIT):
        print('\n Job {0}/{1}'.format(i//LIMIT, N))
        task = dask.persist(extract_app[i: i+LIMIT])
        progress(task)
    print('\n Decomposed')
    return _signout(client)
