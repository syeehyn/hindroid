import os
from scipy import sparse
import json
from glob import glob
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, fbeta_score, accuracy_score, confusion_matrix
from .hindroid import _load_mat, hindroid
from joblib import dump, load
from src import *
APP_REF = 'processed/matrices/ref/app_ref.csv'
def _get_labels(test, APP_REF):
        if test:
            app_ref = os.path.join(ROOT_DIR, 'data/tests', APP_REF)
        else:
            app_ref = os.path.join(ROOT_DIR, 'data/datasets', APP_REF)
        return pd.read_csv(app_ref).sort_values('app_id')['malware'].values
def evaluate(test=False, test_size=.33, methods=['AA', 'ABA', 'APA', 'APBPA'], iterations = 10):
    X, _, _ = _load_mat(test)
    y = _get_labels(test, APP_REF)
    train_res_lst, test_res_lst = [], []
    for _ in range(iterations):
        X_train, X_test, y_train, y_test = \
                train_test_split(X, y, test_size=test_size)
        train_res, test_res = [], []
        for method in methods:
            clf = hindroid(test, method)
            clf.fit(X_train, y_train)
            y_preds = [clf.predict(X_train), clf.predict(X_test)]
            y_trues = [y_train, y_test]
            res = []
            for y_true, y_pred in zip(y_trues, y_preds):
                f1 = f1_score(y_true, y_pred)
                acc = accuracy_score(y_true, y_pred)
                tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
                res += [{
                        'method': method,
                        'f1': f1,
                        'acc': acc,
                        'tp': tp,
                        'fp': fp,
                        'tn': tn,
                        'fn': fn
                            }]
            train_res.append(res[0])
            test_res.append(res[1])
        train_res_lst.append(pd.DataFrame(train_res))
        test_res_lst.append(pd.DataFrame(test_res))
    mean_train_res = pd.concat(train_res_lst).groupby('method').mean()
    mean_test_res = pd.concat(test_res_lst).groupby('method').mean()
    return mean_train_res, mean_test_res