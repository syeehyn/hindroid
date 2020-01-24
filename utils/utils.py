import os
import re
import subprocess
import glob
import requests
import bs4
import gzip
import io
import pandas as pd
from multiprocess import Pool
from tqdm import tqdm
def setup_env():
    """[setting up environment]
    """    
    if not os.path.exists('./data'):
        os.mkdir('./data')
def get_xmls(url):
    """[get xml of the sitemap]
    Returns:
        [list] -- [list of xml.gz]
    """    
    resp = requests.get(url)
    soup = bs4.BeautifulSoup(resp.text, 'lxml')
    groups = soup.findAll('loc')[5:]
    return [i.text for i in groups]
def create_xml_df(xml):
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
def create_sitemap_df(**cfg):
    """[create the metadata of the sitemap]
    """    
    url, fp, nw = cfg['url'], cfg['dir'], cfg['NUM_WORKERS']
    if not os.path.exists('./data/'):
        setup_env()
    if not os.path.exists(fp + '/'):
        os.mkdir(fp)
    xmls = get_xmls(url)
    
    with Pool(nw) as p:
        df_list = list(tqdm(p.imap_unordered(create_xml_df, xmls), total = len(xmls), position=0, leave=True))
    metadata = pd.concat(df_list, ignore_index=True)
    metadata.to_csv(fp + '/metadata.csv',index = False)
def download_app(url, op, app):
    """[download a apk file to the output path]
    Arguments:
        url {[string]} -- [url link of the file]
        op {[string]} -- [output file path]
    """'''    '''
    url += '/download?from=details'
    resp = requests.get(url)
    if not os.path.exists(op + '/' + app):
        os.mkdir(op + '/' + app)
    try:
        soup = bs4.BeautifulSoup(resp.text, 'html.parser')
        download_link = soup.find("iframe", {"id": "iframe_download"})['src']
        resp = requests.get(download_link)
        data = resp.content
        with open(op + '/' + app + '/' + app + '.apk', 'wb') as fh:
            fh.write(data)
    except AttributeError:
        pass
def get_data(**cfg):
    """[download and extract the apks]
    """    
    fp, urls, verbose = cfg['dir'], cfg['urls'], cfg
    if not os.path.exists(fp + '/'):
        os.mkdir(fp + '/')
    for url in urls:
        app = re.findall(r'https:\/\/apkpure.com\/(.*?)\/', url)[0]
        download_app(url, fp, app)
        apk_dir = fp + '/' + app + '/' + app + '.apk'
        op = fp + '/' + app + '/' + app
        if verbose:
            print('fetched {}, start decoding'.format(apk_dir))
            command = subprocess.run([
                'apktool', 'd', 
                apk_dir,
                '-o', op], capture_output = True)
            print(command.stdout.decode())
        else:
            command = subprocess.run([
                'apktool', 'd', 
                apk_dir,
                '-o', op])
        