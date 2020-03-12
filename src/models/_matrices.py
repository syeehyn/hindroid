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
NUM_WORKER = psutil.cpu_count(logical = False)//2
ROOT_DIR = Path(__file__).parent.parent.parent
FP_processed  = 'processed/'
FP_matrices  = 'processed/matrices'
FP_b = 'interim/b_features/*'
FP_m = 'interim/m_features/*'
FP_A = 'processed/matrices/A'
FP_B = 'processed/matrices/B'
FP_P = 'processed/matrices/P'
FP_REF = 'processed/matrices/ref'
FP_pram = os.path.join(ROOT_DIR, 'config/train-params.json')
FP_pram_test = os.path.join(ROOT_DIR, 'config/test-train .json')
def _env_checker(fp_processed, fp_matrices, fp_b, fp_m, fp_ref):
    if not os.path.exists(fp_processed):
        os.mkdir(fp_processed)
    if not os.path.exists(fp_matrices):
        os.mkdir(fp_matrices)
    if not os.path.exists(fp_ref):
        os.mkdir(fp_ref)
    return
# ref = os.path.join(fp_A, 'A_ref.json')
# mat = os.path.join(fp_A, 'A.npz')
def _file_module(test, FP_processed, FP_matrices, FP_b, FP_m, FP_A, FP_B, FP_P, FP_REF):
    if test:
        fp_processed = os.path.join(ROOT_DIR, 'data/tests', FP_processed)
        fp_matrices = os.path.join(ROOT_DIR, 'data/tests', FP_matrices)
        fp_b = os.path.join(ROOT_DIR, 'data/tests', FP_b)
        fp_m = os.path.join(ROOT_DIR, 'data/tests', FP_m)
        fp_A = os.path.join(ROOT_DIR, 'data/tests', FP_A)
        fp_B = os.path.join(ROOT_DIR, 'data/tests', FP_B)
        fp_P = os.path.join(ROOT_DIR, 'data/tests', FP_P)
        fp_ref = os.path.join(ROOT_DIR, 'data/tests', FP_REF)
    else:
        fp_processed = os.path.join(ROOT_DIR, 'data/datasets', FP_processed)
        fp_matrices = os.path.join(ROOT_DIR, 'data/datasets', FP_matrices)
        fp_b = os.path.join(ROOT_DIR, 'data/datasets', FP_b)
        fp_m = os.path.join(ROOT_DIR, 'data/datasets', FP_m)
        fp_A = os.path.join(ROOT_DIR, 'data/datasets', FP_A)
        fp_B = os.path.join(ROOT_DIR, 'data/datasets', FP_B)
        fp_P = os.path.join(ROOT_DIR, 'data/datasets', FP_P)
        fp_ref = os.path.join(ROOT_DIR, 'data/datasets', FP_REF)
    return fp_processed, fp_matrices, fp_b, fp_m, fp_A, fp_B, fp_P, fp_ref

def construct_matrices(test, compute_A, compute_B, compute_P):
    client = Client(n_workers = NUM_WORKER)
    fp_processed, fp_matrices, fp_b, fp_m, fp_A, fp_B, fp_P, fp_ref = _file_module(test, FP_processed, FP_matrices, FP_b, FP_m, FP_A, FP_B, FP_P, FP_REF)
    _env_checker(fp_processed, fp_matrices, fp_b, fp_m, fp_ref)
    print('Start Preprocessing Data')
    if test and os.path.exists(FP_pram_test):
        files = json.load(open(FP_pram_test))
        print('using app list of parameter to train (tests)')
        df_b = dd.concat([dd.read_csv(i) for i in files['benign']])
        df_m = dd.concat([dd.read_csv(i) for i in files['malware']])
    elif (not test) and os.path.exists(FP_pram):
        files = json.load(open(FP_pram))
        print('using app list of parameter to train (datasets)')
        df_b = dd.concat([dd.read_csv(i) for i in files['benign']])
        df_m = dd.concat([dd.read_csv(i) for i in files['malware']])
    else:
        df_b = dd.read_csv(fp_b, usecols = ['api', 'block', 'app'], dtype = str)
        df_m = dd.read_csv(fp_m, usecols = ['api', 'block', 'app'], dtype = str)
    df = df_b.append(df_m).reset_index()
    df = df.dropna()
    apis = df.api.unique().compute()
    apis_dic = {apis.iloc[i]:i for i in range(len(apis))}
    df['api_id'] = df.api.apply(lambda x: apis_dic[x], meta = int)
    df['package'] = df.api.str.split('->').apply(lambda x: x[0] if type(x) == list else x, meta = str)
    with open(os.path.join(fp_ref, 'api_ref.json'), 'w') as fp:
                json.dump(apis_dic, fp)
    df['api_id'] = df.api.apply(lambda x: apis_dic[x], meta = int)
    shape = (len(apis), len(apis))
    print('Finished Preprocessing')
    ###matA
    if compute_A:
        print('\n Constructing Matrix A')
        A, apps = _matrix_A(df, apis)
        sparse.save_npz(fp_A, A)
        with open(os.path.join(fp_ref, 'app_ref.json'), 'w') as fp:
            json.dump(apps, fp)
        print('\n Matrix A Constructed')
    ###matB
    if compute_B:
        print('\n Constructing Matrix B')
        sparse.save_npz(fp_B, _matrix_BP(df, True, shape))
        print('\n Matrix B Constructed')
    ###matP
    if compute_P:
        print('\n Constructing Matrix P')
        sparse.save_npz(fp_P, _matrix_BP(df, False, shape))
        print('\n Matrix P Constructed')
def _matrix_A(df, apis):
    """[summary]
    Returns:
        [string] -- [succesful message]
    """
    print('--Gettng API Set of Each App')
    app_set = df.groupby(['app']).api.apply(lambda x: set(x), meta = 'set')
    app_set = app_set.compute()
    apps = app_set.index.tolist()
    A = np.zeros((len(apps), len(apis)))
    print('\n --A Constructing')
    app_dict = {}
    for i in tqdm(range(len(apps))):
        A[i, np.array(apis.loc[apis.isin(app_set[apps[i]].intersection(set(apis)))].index)] = 1
        app_dict[apps[i]] = i
    A = sparse.coo_matrix(A)
    return A, app_dict

def _matrix_BP(df, is_B, shape):
    if is_B:
        group_key = 'block'
    else:
        group_key = 'package'
    result = df.groupby(group_key).api_id\
            .apply(lambda x: list(combinations(x.drop_duplicates(), 2)), meta = list)\
            .explode()\
            .reset_index(drop = True)\
            .drop_duplicates()\
            .dropna().compute()
    entries = pd.DataFrame(result.values.tolist()).values
    values = np.full(shape=entries.shape[0], fill_value=1, dtype='i1')
    result = sparse.coo_matrix(
                (values, (entries[:,0], entries[:,1])), shape=(shape)
    )
    result.setdiag(1)
    return result