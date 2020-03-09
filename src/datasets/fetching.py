import sys
sys.path.append('../src')
import os
from dask.distributed import Client
from dask import delayed
import dask
from tqdm import tqdm
from src.utils import _decompose_app
from src.utils import _download_app
import json
import re
from pathlib import Path
import psutil
NUM_WORKER = psutil.cpu_count(logical = False)
ROOT_DIR = Path(__file__).parent.parent.parent
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
    apps = {get_app_name(i):{'download':'', 'decode':''} for i in urls}
    for i in tqdm(range(0, len(downloading), NUM_WORKER)):
        proc_downloading = downloading[i: i + NUM_WORKER]
        app = dask.compute(proc_downloading)[0]
        for j in app:
            apps[j[0]]['download'] = j[1]
    extract_app = []
    for app in apps.keys():
        if apps[app]['download'] == 'failed':
            apps[app]['decode'] = 'failed'
        else:
            extract_app.append(app)
    extract_app = [delayed(_decompose_app)(fp, app, clean,verbose) for app in extract_app]
    for i in tqdm(range(0, len(extract_app), NUM_WORKER)):
        proc_extract_app = extract_app[i: i + NUM_WORKER]
        app = dask.compute(proc_extract_app)[0]
        for j in app:
            apps[j]['decode'] = 'done'
    client.close()
    return 'apk download and decode finished'
    