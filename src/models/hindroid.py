import json
from scipy import sparse
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import os
import pandas as pd
from glob import glob
from pathlib import Path
from src import *
MAT_path = 'processed/matrices'
def _load_mat(test):
        if test:
            mat_path = os.path.join(ROOT_DIR, 'data/tests', MAT_path)
        else:
            mat_path = os.path.join(ROOT_DIR, 'data/datasets', MAT_path)
        matA, matB, matP = [sparse.load_npz(os.path.join(mat_path, mat))
            for mat in ['A.npz', 'B.npz', 'P.npz']]
        return matA, matB, matP

class hindroid():
    def __init__(self, test, method):
        _, self.B, self.P = _load_mat(test)
        self.clf = SVC(kernel="precomputed")
        if method == 'AA':
            self.kernel = lambda x,y: x.dot(y.T).todense()
        elif method == 'ABA':
            self.kernel = lambda x,y: x.dot(self.B).dot(y.T).todense()
        elif method == 'APA':
            self.kernel = lambda x,y: x.dot(self.P).dot(y.T).todense()
        elif method == 'APBPA':
            self.kernel = lambda x,y: x.dot(self.P).dot(self.B).dot(self.P.T).dot(y.T).todense()
        else:
            raise NotImplementedError
    def fit(self, X, y):
        _X = self.kernel(X, X)
        self.X = X
        self.y = y
        self.clf.fit(_X, self.y)
    def predict(self, X):
        _X = self.kernel(X, self.X)
        return self.clf.predict(_X)
    def score(self, X, y):
        _X = self.kernel(X, self.X)
        return self.clf.score(_X, y)