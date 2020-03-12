import json
import pandas as pd
import numpy as np
import sys
from itertools import combinations
def main(targets):
    if 'run' in targets:
        b_dir = json.load(open('./config/train-params.json'))['benign']
        m_dir = json.load(open('./config/train-params.json'))['malware']
        apis = json.load(open('/datasets/home/87/887/shy166/dsc180a/hindroid/data/datasets/processed/matrices/ref/api_ref.json'))
        app_dir = b_dir + m_dir
        output = np.array([np.NaN, np.NaN])
        counter = 542
        for i in app_dir[542:]:
            print(counter)
            df = pd.read_csv(i)
            df = df.dropna(subset = ['api'])
            df['api_id'] = df.api.apply(lambda x: apis[x])
            df['package'] = df.api.str.split('->').apply(lambda x: x[0] if type(x) == list else x)
            mat = pd.DataFrame(df.groupby('package').api_id\
                        .apply(lambda x: list(combinations(x.drop_duplicates(), 2)))\
                        .explode()\
                        .reset_index(drop = True)\
                        .drop_duplicates()\
                        .dropna().values.tolist()).values
            if len(mat) == 0:
                counter += 1
                continue
            output = np.unique(np.vstack([output, mat]), axis = 1)
            counter += 1
            np.save('tmp', output)




if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)