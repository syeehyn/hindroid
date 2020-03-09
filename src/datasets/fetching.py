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
from pathlib import Path
import psutil
import logging
logger = logging.getLogger("distributed.utils_perf")
logger.setLevel(logging.ERROR)
NUM_WORKER = psutil.cpu_count(logical = False)
ROOT_DIR = Path(__file__).parent.parent.parent

def _signout(clt):
    clt.close()
    return
def _initilize_dataenv(fp):
    filepath = fp
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    if not os.path.exists(os.path.join(filepath, 'raw/apps')):
        os.mkdir(os.path.join(filepath, 'raw'))
        os.mkdir(os.path.join(filepath, 'raw/apps'))
        os.mkdir(os.path.join(filepath, 'raw/smali'))

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
    _initilize_dataenv(fp)
    get_app_name = lambda url: re.findall(r'https:\/\/apkpure.com\/(.*?)\/', url)[0]
    downloading = [delayed(_download_app)(url, fp, get_app_name(url)) for url in urls]
    task = dask.persist(downloading)
    print('Downloading')
    progress(task)
    print('\n Downloaded')
    extract_app = [i.split('/')[-1] for i in glob(os.path.join(fp, 'raw/apps/*'))]
    extract_app = [delayed(_decompose_app)(fp, app, clean,verbose) for app in extract_app]
    print('Total {} apk will be extracted'.format(len(extract_app)))
    task = dask.persist(extract_app)
    progress(task)
    print('\n Decomposed')
    return _signout(client)
