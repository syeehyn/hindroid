from pyspark.sql import SparkSession
from pyspark import SparkContext
import pyspark.ml as M
import pyspark.sql.functions as F
import pyspark.sql.types as T
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
from src import *
FP_b = 'interim/b_features/*.csv'
FP_m = 'interim/m_features/*.csv'
FP_pram = os.path.join(ROOT_DIR, 'config/train-params.json')
FP_pram_test = os.path.join(ROOT_DIR, 'config/test-train .json')
def _preproc(test, FP_b, FP_m):
    SparkContext.setSystemProperty('spark.executor.memory', '64g')
    sc = SparkContext("local", "App Name")
    sc.setLogLevel("ERROR")
    spark = SparkSession(sc)
    spark.conf.set('spark.ui.showConsoleProgress', True)
    spark.conf.set("spark.sql.shuffle.partitions", NUM_WORKER)
    if test:
        fp_b = os.path.join(ROOT_DIR, 'data/tests', FP_b)
        fp_m = os.path.join(ROOT_DIR, 'data/tests', FP_m)
    else:
        fp_b = os.path.join(ROOT_DIR, 'data/datasets', FP_b)
        fp_m = os.path.join(ROOT_DIR, 'data/datasets', FP_m)
    print('Start Preprocessing Data')
    if test and os.path.exists(FP_pram_test):
        files = json.load(open(FP_pram_test))
        print('using app list of parameter to train (tests)')
        df_b = spark.read.format("csv").option("header", "true").load(files['benign'])
        df_m = spark.read.format("csv").option("header", "true").load(files['malware'])
    elif (not test) and os.path.exists(FP_pram):
        files = json.load(open(FP_pram))
        print('using app list of parameter to train (datasets)')
        df_b = spark.read.format("csv").option("header", "true").load(files['benign'])
        df_m = spark.read.format("csv").option("header", "true").load(files['malware'])
    else:
        df_b = spark.read.format("csv").option("header", "true").load(fp_b)
        df_m = spark.read.format("csv").option("header", "true").load(fp_m)
    df = df_b.union(df_m)
    df = df.dropna()
    df = df.select('api', 'app', 'block', 'malware', 'invocation')
    df = df.withColumn('package', F.split(F.col('api'), '->')[0])
    output = df.groupby('app').agg(
                    F.countDistinct(F.col('api')).alias('api'),
                    F.countDistinct(F.col('block')).alias('block'),
                    F.countDistinct(F.col('package')).alias('package'),
                    F.mean(F.col('malware')).cast('int').alias('malware'))
    most_api = df.groupby(['app', 'api']).count()\
                .groupby('app').agg(F.max(F.struct(F.col('count'),
                                          F.col('api'))).alias('max'))\
                .select(F.col('app'), F.col('max.api').alias('most_api'))
    most_package = df.groupby(['app', 'package']).count()\
                .groupby('app').agg(F.max(F.struct(F.col('count'),
                                          F.col('package'))).alias('max'))\
                .select(F.col('app'), F.col('max.package').alias('most_package'))
    output = output.join(most_api, ['app']).join(most_package, ['app']).toPandas()
    return output
def baseline(test, clf, df):
    num_feat = ['api', 'block', 'package']
    num_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
    cat_feat = ['most_api', 'most_package']
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
    train_res, test_res = [], []
    for clf in clfs:
        model = baseline(test, clf, df)
        model.fit(X_train, y_train)
        y_preds = [model.predict(X_train), model.predict(X_test)]
        y_trues = [y_train, y_test]
        res = []
        for y_true, y_pred in zip(y_trues, y_preds):
            f1 = f1_score(y_true, y_pred)
            acc = accuracy_score(y_true, y_pred)
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
            res += [{
                    'method': type(clf).__name__,
                    'f1': f1,
                    'acc': acc,
                    'tp': tp,
                    'fp': fp,
                    'tn': tn,
                    'fn': fn
                        }]
        train_res.append(res[0])
        test_res.append(res[1])
    return pd.DataFrame(train_res), pd.DataFrame(test_res)

    