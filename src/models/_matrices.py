import os
import pandas as pd
import numpy as np
from pyspark.sql import SparkSession
from pyspark import SparkContext
import pyspark.ml as M
import pyspark.sql.functions as F
import pyspark.sql.types as T
import databricks.koalas as ks
from scipy import sparse
from pathlib import Path
import json
import psutil
NUM_WORKER = psutil.cpu_count(logical = False)
SparkContext.setSystemProperty('spark.executor.memory', '64g')
sc = SparkContext("local", "App Name")
sc.setLogLevel("ERROR")
spark = SparkSession(sc)
spark.conf.set('spark.ui.showConsoleProgress', True)
spark.conf.set("spark.sql.shuffle.partitions", NUM_WORKER)
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
    fp_processed, fp_matrices, fp_b, fp_m, fp_A, fp_B, fp_P, fp_ref = _file_module(test, FP_processed, FP_matrices, FP_b, FP_m, FP_A, FP_B, FP_P, FP_REF)
    _env_checker(fp_processed, fp_matrices, fp_b, fp_m, fp_ref)
    print('Start Preprocessing Data')
    if test and os.path.exists(FP_pram_test):
        files = json.load(open(FP_pram_test))
        print('using app list of parameter to train (tests)')
        df_b = ks.read_csv(files['benign'])
        df_m = ks.read_csv(files['malware'])
    elif (not test) and os.path.exists(FP_pram):
        files = json.load(open(FP_pram))
        print('using app list of parameter to train (datasets)')
        df_b = ks.read_csv(files['benign'])
        df_m = ks.read_csv(files['malware'])
    else:
        df_b = ks.read_csv(fp_b)
        df_m = ks.read_csv(fp_m)
    df = df_b.append(df_m).reset_index()
    df = df.dropna()
    df = df.to_spark()
    df = df.select('api', 'app', 'block')
    df = df.withColumn('package', F.split(F.split(F.col('api'), '->')[0], '/')[0])
    num_app, num_api, num_block, num_package = df.select(F.countDistinct('app'),
                                                            F.countDistinct('api'),
                                                            F.countDistinct('block'),
                                                            F.countDistinct('package')).head()
    stringIndexer = M.feature.StringIndexer(inputCol='api', outputCol='api_id')
    model = stringIndexer.fit(df)
    df = model.transform(df)
    ###
    stringIndexer = M.feature.StringIndexer(inputCol='app', outputCol='app_id')
    model = stringIndexer.fit(df)
    df = model.transform(df)
    stringIndexer = M.feature.StringIndexer(inputCol='block', outputCol='block_id')
    model = stringIndexer.fit(df)
    df = model.transform(df)
    stringIndexer = M.feature.StringIndexer(inputCol='package', outputCol='package_id')
    model = stringIndexer.fit(df)
    df = model.transform(df)
    api_o = df.select('api', 'app', 'block', 'package')
    com = df.select(F.col('api_id').alias('api'),
                F.col('app_id').alias('app'),
                F.col('block_id').alias('block'),
                F.col('package_id').alias('package')
                    )
    A_prec = com.select('api', 'app').dropDuplicates()
    B_prec = com.select('api', 'block').dropDuplicates()
    P_prec = com.select('api', 'package').dropDuplicates()
    if compute_A:
        A = A_prec.toPandas().values.astype(int)
        values = np.full(shape=A.shape[0], fill_value=1, dtype='i1')
        A = sparse.coo_matrix(
                        (values, (A[:,1], A[:,0])), shape=(num_app, num_api)
            )
        sparse.save_npz(fp_A, A)
        print('finished constructing A')
    if compute_B:
        B = B_prec.toPandas().values.astype(int)
        values = np.full(shape=B.shape[0], fill_value=1, dtype='i1')
        B = sparse.coo_matrix(
                        (values, (B[:,1], B[:,0])), shape=(num_block, num_api)
            ).T
        B = (B.dot(B.T) > 0).astype(int)
        sparse.save_npz(fp_B, B)
        print('finished constructing B')
    if compute_P:
        P = P_prec.toPandas().values.astype(int)
        values = np.full(shape=P.shape[0], fill_value=1, dtype='i1')
        P = sparse.coo_matrix(
                        (values, (P[:,1], P[:,0])), shape=(num_package, num_api)
            ).T
        P = (P.dot(P.T) > 0).astype(int)
        sparse.save_npz(fp_P, P)
        print('finished constructing P')
