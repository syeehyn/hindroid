import json
from scipy import sparse
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import os
import pandas as pd
from glob import glob
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent.parent
API_REF = 'processed/matrices/ref/api_ref.json'
APP_REF = 'processed/matrices/ref/app_ref.json'
M_path = 'interim/m_features/*.csv'
MAT_path = 'processed/matrices'
def _get_labels(test):
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

class hindroid():
    def __init__(self, test, metapath):
        _, self.B, self.P = self._load_mat(test)
        self.clf = SVC(kernel="precomputed")
        if metapath == 'AA':
            self.kernel = lambda x,y: x.dot(y.T).todense()
        elif metapath == 'ABA':
            self.kernel = lambda x,y: x.dot(self.B).dot(y.T).todense()
        elif metapath == 'APA':
            self.kernel = lambda x,y: x.dot(self.P).dot(y.T).todense()
        elif metapath == 'APBPA':
            self.kernel = lambda x,y: x.dot(self.P).dot(self.B).dot(self.P.T).dot(y.T)
        else:
            raise NotImplementedError
    def _load_mat(self, test):
        if test:
            mat_path = os.path.join(ROOT_DIR, 'data/tests', MAT_path)
        else:
            mat_path = os.path.join(ROOT_DIR, 'data/datasets', MAT_path)
        matA, matB, matP = [sparse.load_npz(mat_path)
            for mat in ['A.npz', 'B.npz', 'P.npz']]
        return matA, matB, matP
    def fit(self, X, y):
        self.X = self.kernel(X, X)
        self.y = y
        self.clf.fit(self.X, self.y)
    def predict(self, X):
        _X = self.kernel(X, X)
        return self.clf.predict(_X)
    def score(self, X, y):
        _X = self.kernel(X, X)
        return self.clf.score(_X, y)