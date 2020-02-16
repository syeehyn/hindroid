import dask
from dask.distributed import Client
import dask.dataframe as dd
import pandas as pd
import numpy as np
import json
from tqdm import tqdm
from scipy import sparse
def matrix_A(**cfg):
    """[summary]
    Arguments:
        fp {[string]} -- [csv file directory]
        ref {[string]} -- [output reference file directory (.json)]
        mat {[string]} -- [output matrix file directory (.npz)]
    Returns:
        [string] -- [succesful message]
    """    
    client = Client(n_workers = 8)
    fp, ref, mat= cfg['fp'], cfg['ref'], cfg['mat']
    df = dd.read_csv(fp)
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