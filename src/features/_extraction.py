import os
import re
from glob import glob
import numpy as np
import pandas as pd
from tqdm import tqdm
import dask
from dask import delayed
pd.options.mode.chained_assignment = None
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
def _get_app_info(fp, app, malware, op):
    # job_queue = [delayed(_get_method_call)(fn) for fn in _get_app_smali_dir(fp, app)]
    # agg = dask.compute(job_queue)[0]
    agg = [_get_method_call(fn) for fn in _get_app_smali_dir(fp, app)]
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
    df.loc[:, 'block'] = df['method'] + df['smali']
    df = pd.concat([df, df.call.str.extract(pattern)\
            .rename(columns={0: 'invocation', 1: 'package', 2: 'method_name'})], axis = 1)\
            .drop(['call', 'method', 'smali'], axis = 1)\
            .reset_index(drop = True).drop_duplicates()
    df.loc[:, 'api'] = (df['package'] + '->' + df['method_name'])
    df = df[['api', 'invocation', 'block']]
    df.loc[:, 'app'] = app
    df.loc[:, 'malware'] = malware
    df.to_csv(os.path.join(op, app + '.csv'), index = False)
    return 'done'