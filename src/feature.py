import numpy as np
import pandas as pd
from glob import glob
import os
import re
from tqdm import tqdm
import pandas as pd
from multiprocess import Pool
from dask.distributed import Client
from dask import delayed
import shutil
import json
import dask
import logging
logger = logging.getLogger("distributed.utils_perf")
logger.setLevel(logging.ERROR)
def _get_app_smali_dir(fp, app):
    app_dir = os.path.join(fp, app)
    return sorted(glob(os.path.join(app_dir, 'smali*/**/*.smali'), recursive=True))
def _get_method_call(fn):
    with open(fn) as f:
        pattern = r'\.method\s+(.*)|(invoke-.*)'
        data = re.findall(pattern, f.read())
        if len(data) == 0: return pd.DataFrame()
        data = pd.DataFrame(np.array(data), columns = ['method', 'call']).replace('', np.NaN)
        data['method'] = data['method'].fillna(method = 'ffill')
        data['smali'] = [fn.split('/')[-1] for _ in range(len(data))]
    return data.dropna()
def _get_app_info(fp, app):
    job_queue = [delayed(_get_method_call)(fn) for fn in _get_app_smali_dir(fp, app)]
    agg = dask.compute(job_queue)[0]
#     agg = [get_method_call(fn) for fn in get_app_smali_dir(fp, app)]
    if agg == None:
        return pd.DataFrame()
    agg = [i for i in agg if len(i) != 0]
    if len(agg) == 0:
        return pd.DataFrame()
    df = pd.concat(agg, ignore_index = True).drop_duplicates()
    pattern =  (
        "(invoke-\w+)(?:\/range)? {.*}, "     # invoke
        + "(\[*[ZBSCFIJD]|\[*L[\w\/$-]+;)->"   # package
        + "([\w$]+|<init>).+"                 # method
    )
    df['block'] = df['method'] + df['smali']
    df = pd.concat([df, df.call.str.extract(pattern)\
            .rename(columns={0: 'invocation', 1: 'package', 2: 'method_name'})], axis = 1)\
            .drop(['call', 'method', 'smali'], axis = 1)\
            .reset_index(drop = True).drop_duplicates()
    return df
def get_apps_info(**cfg):
    """[extract basic features of apps]
    Arguments:
        fp {[string]} -- [app target download directory]
        map_dir {[string]} -- [app map file directory]
        op {[string]} -- [output file directory]
    Returns:
        [type] -- [description]
    """
    client = Client()
    client.restart()
    print("Dashboard Address: " + 'http://127.0.0.1:' + str(client.scheduler_info()['services']['dashboard'])+'/status')
    fp, map_dir, op = cfg['fp'], cfg['map_dir'], cfg['op']
    app_map = pd.Series(json.load(open(map_dir))).apply(lambda x: x['decode'])
    applist = list(app_map[app_map == 'done'].index)
    op_csv = [i.split('/')[-1][:-4] for i in glob(op + '/*.csv')]
    for app in tqdm(applist):
        if app not in op_csv:
            df = _get_app_info(fp, app)
            if len(df) != 0:
                df['app'] = app
                df.to_csv(os.path.join(op, app + '.csv'), index = False)
    return 'api calls extracted'

def extract_malware(**cfg):
    fp, op= cfg['fp'], cfg['op']
    apps = [i.split('/')[-1] for i in glob(fp + '/*')]
    apps = {i: {"download": "success", "decode": "done"}for i in apps}
    os.mkdir("tmp")
    with open("tmp/malwareapps.json", 'w') as f:
        json.dump(apps, f)
    config = {
        "fp": fp,
        "map_dir": "tmp/malwareapps.json",
        "op": op
    }
    get_apps_info(**config)
    shutil.rmtree("tmp")