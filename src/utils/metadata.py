import io
import os
import pandas as pd
import requests
import bs4
import gzip
from tqdm import tqdm
from multiprocessing import Pool
import json
from pathlib import Path
import psutil
from src import *
URL = "https://apkpure.com/sitemap.xml"
OP = os.path.join(ROOT_DIR, 'data/metadata/metadata.csv')
def _get_xmls(url):
    """[get xml of the sitemap]
    Returns:
        [list] -- [list of xml.gz]
    """    
    resp = requests.get(url)
    soup = bs4.BeautifulSoup(resp.text, 'lxml')
    groups = soup.findAll('loc')[5:]
    return [i.text for i in groups]
def _create_xml_df(xml):
    """[get the data frame of xml.gz]
    Arguments:
        xml {[string]} -- [the gz compression of xml link]
    
    Returns:
        [pd.DataFrame] -- [the dataframe of the xml link]
    """    
    response = requests.get(xml).content
    urlText = io.StringIO(gzip.decompress(response).decode())
    soup = bs4.BeautifulSoup(urlText, 'lxml')
    loc = soup.findAll('loc')
    lastmod = soup.findAll('lastmod')
    changefreq = soup.findAll('changefreq')
    priority = soup.findAll('priority')
    return pd.DataFrame({
        'loc': [i.text for i in loc],
        'lastmod': [i.text for i in lastmod],
        'changefreq': [i.text for i in changefreq],
        'priority': [i.text for i in priority],
        'sitemap_url': [xml for i in loc]
    })
def _initilize_dataenv(fp):
    """[create the dataset directory tree]
    Arguments:
        fp {[string]} -- [input data directory]
    """ 
    if os.path.exists(os.path.join(fp, 'data/')):
        return
    else:
        os.mkdir(os.path.join(fp, 'data/'))
        os.mkdir(os.path.join(fp,'data/metadata/'))
        os.mkdir(os.path.join(fp,'data/datasets/'))
        os.mkdir(os.path.join(fp,'data/datasets/raw/'))
        os.mkdir(os.path.join(fp,'data/datasets/interim/'))
        os.mkdir(os.path.join(fp,'data/datasets/processed/'))
        os.mkdir(os.path.join(fp,'data/datasets/external/'))
        os.mkdir(os.path.join(fp,'data/tests/'))
        os.mkdir(os.path.join(fp,'data/tests/raw/'))
        os.mkdir(os.path.join(fp,'data/tests/interim/'))
        os.mkdir(os.path.join(fp,'data/tests/processed/'))
        os.mkdir(os.path.join(fp, 'data/tests/external/'))
def create_metadata():
    """[create the metadata of the sitemap]
    """
    fp = ROOT_DIR
    _initilize_dataenv(fp)
    xmls = _get_xmls(URL)
    with Pool(NUM_WORKER) as p:
        df_list = list(tqdm(p.imap_unordered(_create_xml_df, xmls), total = len(xmls), position=0, leave=True))
    metadata = pd.concat(df_list, ignore_index=True)
    metadata.to_csv(OP, index = False)