import dask
from dask.distributed import Client
import dask.dataframe as dd
import pandas as pd
import numpy as np
import json
from tqdm import tqdm
from scipy import sparse
import psutil
NUM_WORKER = psutil.cpu_count(logical = False)
def _matrix_A(**cfg):
    """[summary]
    Arguments:
        fp_b {[string]} -- [benign csv file directory]
        fp_m {[string]} -- [malware csv file directory]
        ref {[string]} -- [output reference file directory (.json)]
        mat {[string]} -- [output matrix file directory (.npz)]
    Returns:
        [string] -- [succesful message]
    """    
    client = Client(n_workers = NUM_WORKER)
    fp_b, fp_m, ref, mat= cfg['fp_b'], cfg['fp_m'], cfg['ref'], cfg['mat']
    df_b = dd.read_csv(fp_b)
    df_m = dd.read_csv(fp_m)
    df = df_b.append(df_m).reset_index()
    df['api'] = (df['package'] + '->' + df['method_name'])
    app_set = df.groupby(['app']).api.apply(lambda x: set(x), meta = 'set').compute()
    apis = df.api.unique().compute()
    apps = app_set.index.tolist()
    A = np.zeros((len(apps), len(apis)))
    for i in tqdm(range(len(apps))):
        A[i, np.array(apis.loc[apis.isin(app_set[apps[i]].intersection(set(apis)))].index)] = 1
    A = sparse.coo_matrix(A)
    reference_dic = {'apps': apps, 'apis': apis.tolist()}
    with open(ref, 'w') as fp:
        json.dump(reference_dic, fp)
    sparse.save_npz(mat, A)
    return "Matrix A Constructed"