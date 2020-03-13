import os
from scipy import sparse
import json
from glob import glob
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, fbeta_score, accuracy_score, confusion_matrix
from .hindroid import _load_mat, hindroid
ROOT_DIR = Path(__file__).parent.parent.parent
APP_REF = 'processed/matrices/ref/app_ref.csv'
def _get_labels(test, APP_REF):
        if test:
            app_ref = os.path.join(ROOT_DIR, 'data/tests', APP_REF)
        else:
            app_ref = os.path.join(ROOT_DIR, 'data/datasets', APP_REF)
        return pd.read_csv(app_ref).sort_values('app_id')['malware'].values

def evaluating(test=False, test_size=.33, methods=['AA', 'ABA', 'APA', 'APBPA']):
    X, _, _ = _load_mat(test)
    y = _get_labels(test, APP_REF)
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
            # beta = fbeta_score(y_test, y_pred, average='binary', beta=1)
            acc = accuracy_score(y_true, y_pred)
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
            res += [{
                    'method': method,
                    'f1': f1,
                    # 'beta': beta,
                    'acc': acc,
                    'tp': tp,
                    'fp': fp,
                    'tn': tn,
                    'fn': fn
                        }]
        train_res.append(res[0])
        test_res.append(res[1])
    return pd.DataFrame(train_res), pd.DataFrame(test_res)