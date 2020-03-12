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
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, fbeta_score, accuracy_score, confusion_matrix
NUM_WORKER = psutil.cpu_count(logical = False)
ROOT_DIR = Path(__file__).parent.parent.parent
FP_b = 'interim/b_features/*.csv'
FP_m = 'interim/m_features/*.csv'
FP_pram = os.path.join(ROOT_DIR, 'config/train-params.json')
FP_pram_test = os.path.join(ROOT_DIR, 'config/test-train .json')
def _preproc(test, FP_b, FP_m):
    client = Client(n_workers = NUM_WORKER)
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
                        'package': tunique,
                        'malware': 'mean'
                    } , split_out = NUM_WORKER)
    most_invo = df.groupby('app').invocation.apply(lambda x: x.mode()[0], meta = str)
    most_api = df.groupby('app').api.apply(lambda x: x.mode()[0], meta = str)
    most_package = df.groupby('app').package.apply(lambda x: x.mode()[0], meta = str)
    result = dask.compute([grouped, most_invo, most_api, most_package])
    results = result[0][0]
    results['most_invo'] = result[0][1].tolist()
    results['most_api'] = result[0][2].tolist()
    results['most_package'] = result[0][3].tolist()
    return results
def baseline(test, clf, df):
    num_feat = ['api', 'block', 'package']
    num_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
    cat_feat = ['most_invo', 'most_api', 'most_package']
    cat_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
    preproc = ColumnTransformer(transformers=[('num', num_transformer, num_feat),\
                                                ('cat', cat_transformer, cat_feat)])
    pl = Pipeline(steps=[('preprocessor', preproc),
            ('clf', clf)
            ])
    return pl
def evaluate(test = False, clfs = [LogisticRegression(), SVC(), RandomForestClassifier()], test_size = .33):
    df = _preproc(test, FP_b, FP_m)
    X = df.drop('malware', axis = 1)
    y = df.malware
    X_train, X_test, y_train, y_test = \
            train_test_split(X, y, test_size=test_size)
    results = []
    for clf in clfs:
        model = baseline(test, clf, df)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        f1 = f1_score(y_test, y_pred)
        # beta = fbeta_score(y_test, y_pred, average='binary', beta=1)
        acc = accuracy_score(y_test, y_pred)
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        res = {
                'method': type(clf).__name__,
                'f1': f1,
                # 'beta': beta,
                'acc': acc,
                'tp': tp,
                'fp': fp,
                'tn': tn,
                'fn': fn
                }
        results.append(res)
    return pd.DataFrame(results), len(X)