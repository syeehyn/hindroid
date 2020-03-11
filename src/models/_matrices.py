import os
from itertools import combinations
import dask
from dask import delayed
from dask.distributed import Client, progress
import dask.dataframe as dd
from glob import glob
import pandas as pd
import numpy as np
import json
from tqdm import tqdm
from scipy import sparse
import psutil
from pathlib import Path
NUM_WORKER = psutil.cpu_count(logical = False)
LIMIT = NUM_WORKER * 2
ROOT_DIR = Path(__file__).parent.parent.parent
FP_processed  = 'processed/'
FP_matrices  = 'processed/matrices'
FP_b = 'interim/b_features/*'
FP_m = 'interim/m_features/*'
FP_A = 'processed/matrices/A'
FP_B = 'processed/matrices/B'
_FP_B = 'interim/_B'
FP_P = 'processed/matrices/P'
_FP_P = 'interim/_P'
FP_REF = 'processed/matrices/ref'
def _env_checker(fp_processed, fp_matrices, fp_b, fp_m, _fp_B, _fp_P, fp_ref):
    if not os.path.exists(fp_processed):
        os.mkdir(fp_processed)
    if not os.path.exists(fp_matrices):
        os.mkdir(fp_matrices)
    if not os.path.exists(_fp_B):
        os.mkdir(_fp_B)
    if not os.path.exists(_fp_P):
        os.mkdir(_fp_P)
    if not os.path.exists(fp_ref):
        os.mkdir(fp_ref)
    return
# ref = os.path.join(fp_A, 'A_ref.json')
# mat = os.path.join(fp_A, 'A.npz')
def _file_module(test, FP_processed, FP_matrices, FP_b, FP_m, FP_A, FP_B, _FP_B, FP_P, _FP_P, FP_REF):
    if test:
        fp_processed = os.path.join(ROOT_DIR, 'data/tests', FP_processed)
        fp_matrices = os.path.join(ROOT_DIR, 'data/tests', FP_matrices)
        fp_b = os.path.join(ROOT_DIR, 'data/tests', FP_b)
        fp_m = os.path.join(ROOT_DIR, 'data/tests', FP_m)
        fp_A = os.path.join(ROOT_DIR, 'data/tests', FP_A)
        fp_B = os.path.join(ROOT_DIR, 'data/tests', FP_B)
        _fp_B = os.path.join(ROOT_DIR, 'data/tests', _FP_B)
        fp_P = os.path.join(ROOT_DIR, 'data/tests', FP_P)
        _fp_P = os.path.join(ROOT_DIR, 'data/tests', _FP_P)
        fp_ref = os.path.join(ROOT_DIR, 'data/tests', FP_REF)
    else:
        fp_processed = os.path.join(ROOT_DIR, 'data/datasets', FP_processed)
        fp_matrices = os.path.join(ROOT_DIR, 'data/datasets', FP_matrices)
        fp_b = os.path.join(ROOT_DIR, 'data/datasets', FP_b)
        fp_m = os.path.join(ROOT_DIR, 'data/datasets', FP_m)
        fp_A = os.path.join(ROOT_DIR, 'data/datasets', FP_A)
        fp_B = os.path.join(ROOT_DIR, 'data/datasets', FP_B)
        _fp_B = os.path.join(ROOT_DIR, 'data/datasets', _FP_B)
        fp_P = os.path.join(ROOT_DIR, 'data/datasets', FP_P)
        _fp_P = os.path.join(ROOT_DIR, 'data/datasets', _FP_P)
        fp_ref = os.path.join(ROOT_DIR, 'data/datasets', FP_REF)
    return fp_processed, fp_matrices, fp_b, fp_m, fp_A, fp_B, _fp_B, fp_P, _fp_P, fp_ref

def construct_matrices(test, compute_A, compute_B, compute_P):
    client = Client(n_workers = NUM_WORKER)
    fp_processed, fp_matrices, fp_b, fp_m, fp_A, fp_B, _fp_B, fp_P, _fp_P, fp_ref = _file_module(test, FP_processed, FP_matrices, FP_b, FP_m, FP_A, FP_B, _FP_B, FP_P, _FP_P, FP_REF)
    _env_checker(fp_processed, fp_matrices, fp_b, fp_m, _fp_B, _fp_P, fp_ref)
    print('Start Preprocessing Data')
    df_b = dd.read_csv(fp_b, usecols = ['api', 'block', 'app'], dtype = str)
    df_m = dd.read_csv(fp_m, usecols = ['api', 'block', 'app'], dtype = str)
    df = df_b.append(df_m).reset_index()
    apps = df.app.unique().reset_index().set_index('app').compute()
    apis = df.api.unique().reset_index().set_index('api').compute()
    apps.columns = ['id']
    apis.columns = ['id']
    apps.to_csv(os.path.join(fp_ref, 'app_ref.csv'))
    apis.to_csv(os.path.join(fp_ref, 'api_ref.csv'))
    apps = apps['id']
    apis = apis['id']
    apps_dir = glob(fp_b) + glob(fp_m)
    big_apis = client.scatter(apis)
    print('Finished Preprocessing')
    ###matA
    if compute_A:
        print('Constructing Matrix A')
        sparse.save_npz(fp_A, _matrix_A(df))
        print('Matrix A Constructed')
    ###matB
    if compute_B:
        print('Constructing Matrix B')
        sparse.save_npz(fp_B, _matrix_BP(big_apis, apps_dir, True, _fp_B))
        print('Matrix B Constructed')
    ###matP
    if compute_P:
        print('Constructing Matrix P')
        sparse.save_npz(fp_P, _matrix_BP(big_apis, apps_dir, False, _fp_P))
        print('Matrix P Constructed')
def _matrix_A(df):
    """[summary]
    Returns:
        [string] -- [succesful message]
    """        
    app_set = df.groupby(['app']).api.apply(lambda x: set(x), meta = 'set').compute()
    apps = app_set.index.tolist()
    apis = df.api.unique().compute()
    A = np.zeros((len(apps), len(apis)))
    for i in tqdm(range(len(apps))):
        A[i, np.array(apis.loc[apis.isin(app_set[apps[i]].intersection(set(apis)))].index)] = 1
    A = sparse.coo_matrix(A)
    return A

def _matrix_BP(big_apis, apps_dir, is_B, fp):
    entry_pairs = [delayed(_single_pair)(app, big_apis, is_B, fp) for app in apps_dir]
    entries = []
    N = int(np.ceil(len(entry_pairs) / LIMIT))
    for i in range(0, len(entry_pairs), LIMIT):
        print('\n Job {0}/{1}'.format(i//LIMIT, N))
        jobs = entry_pairs[i: i+LIMIT]
        res = dask.compute(jobs)
        entries = np.vstack(entries + res[0])
        entries = [np.unique(entries, axis = 0)]
    entries = np.unique(entries[0], axis = 0)
    values = np.full(shape=entries.shape[0], fill_value=1, dtype='i1')
    result = sparse.coo_matrix(
                (values, (entries[:,0], entries[:,1])), shape=(len(values), len(values))
    )
    result.setdiag(1)
    return result

def _single_pair(app, apis, is_B, fp):
    if is_B:
        group_key = 'block'
        op_name = app.split('/')[-1] + '_B.npy'
        filepath = os.path.join(fp, op_name)
        if os.path.exists(filepath):
            return np.load(filepath)
        df = pd.read_csv(app, usecols = ['api', 'block'])
        df['api_id'] = df.api.apply(lambda x: apis.loc[x])
    else:
        group_key = 'package'
        op_name = app.split('/')[-1] + '_P.npy'
        filepath = os.path.join(fp, op_name)
        if os.path.exists(filepath):
            return np.load(filepath)
        df = pd.read_csv(app, usecols = ['api'])
        df[group_key] = df.api.str.split('->').apply(lambda x: x[0])
        df['api_id'] = df.api.apply(lambda x: apis.loc[x])
    paires = pd.DataFrame(
                    df.groupby(group_key).api_id\
                        .apply(lambda x: list(combinations(x.drop_duplicates(), 2)))\
                        .explode()\
                        .reset_index(drop = True)\
                        .drop_duplicates()\
                        .dropna()\
                        .values\
                        .tolist())\
                    .values\
                    .astype(int)
    np.save(filepath, paires)
    return paires
        