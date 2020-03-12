import os
from scipy import sparse
import json
from glob import glob
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1, fbeta_score, accuracy_score, confusion_matrix
from .hindroid import _load_mat, hindroid
ROOT_DIR = Path(__file__).parent.parent.parent
API_REF = 'processed/matrices/ref/api_ref.json'
APP_REF = 'processed/matrices/ref/app_ref.json'
M_path = 'interim/m_features/*.csv'
def _get_labels(test, APP_REF, M_path):
        if test:
            app_ref = os.path.join(ROOT_DIR, 'data/tests', APP_REF)
            m_path = os.path.join(ROOT_DIR, 'data/tests', M_path)
        else:
            app_ref = os.path.join(ROOT_DIR, 'data/datasets', APP_REF)
            m_path = os.path.join(ROOT_DIR, 'data/datasets', M_path)
        apps = pd.Series(json.load(open(app_ref))).reset_index().set_index(0)
        apps.columns = ['app']
        apps = app_ref['app']
        m_set = [i.split('/')[-1][:-4] for i in glob(m_path)]
        return apps.apply(lambda x: x in m_set).astype(int).values

def evaluation(test=False, test_size=.33, methods=['AA', 'ABA', 'APA', 'APBPA']):
    X, _, _ = _load_mat(test)
    y = _get_labels(test, APP_REF, M_path)
    X_train, X_test, y_train, y_test = \
            train_test_split(X, y, test_size=test_size)
    for method in methods:
        clf = hindroid(test, method)
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()