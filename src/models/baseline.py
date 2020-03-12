import dask
from dask.distributed import Client
import dask.dataframe as dd
import pandas as pd
import os
import numpy as np
import json
from tqdm import tqdm
from scipy import sparse
import psutil
from pathlib import Path
NUM_WORKER = psutil.cpu_count(logical = False)
ROOT_DIR = Path(__file__).parent.parent.parent
FP_b = 'interim/b_features/*.csv'
FP_m = 'interim/m_features/*.csv'

def _preproc(test, FP_b, FP_m):
    client = Client(n_workers = NUM_WORKER)
    if test:
        fp_b = os.path.join(ROOT_DIR, 'data/tests', FP_b)
        fp_m = os.path.join(ROOT_DIR, 'data/tests', FP_m)
    else:
        fp_b = os.path.join(ROOT_DIR, 'data/datasets', FP_b)
        fp_m = os.path.join(ROOT_DIR, 'data/datasets', FP_m)
    df_b = dd.read_csv(fp_b)
    df_m = dd.read_csv(fp_m)
    df = df_b.append(df_m).reset_index()
    df['package'] = df.api.str.split('->').apply(lambda x: x[0] if type(x) == list else x, meta = str)
    nunique_chunk = lambda s: s.apply(lambda x: list(set(x)))
    nunique_agg = lambda s: s._selected_obj.groupby(level=list(range(s._selected_obj.index.nlevels))).sum()
    unique_finalize = lambda s: s.apply(lambda x: len(set(x)))
    tunique = dd.Aggregation('tunique', nunique_chunk, nunique_agg, unique_finalize)
    grouped = df.groupby('app').agg(
                    {
                        'api': tunique,
                        'block': tunique,
                        'package': tunique
                    } , split_out = NUM_WORKER)
    most_invo = df.groupby('app').invocation.apply(lambda x: x.mode()[0], meta = str)
    most_api = df.groupby('app').api.apply(lambda x: x.mode()[0], meta = str)
    most_package = df.groupby('app').package.apply(lambda x: x.mode()[0], meta = str)
    result = dask.compute([grouped, most_invo, most_api, most_package])
    results = result[0][0]
    results['most_invo'] = result[0][1].tolist()
    results['most_api'] = result[0][2].tolist()
    results['most_package'] = result[0][3].tolist()
    return result