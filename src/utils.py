import os
import re
import subprocess
from glob import glob
import requests
import bs4
import gzip
import io
import shutil
import pandas as pd
from multiprocess import Pool
from tqdm import tqdm
import json
from dask.distributed import Client, LocalCluster
from dask import delayed
import dask
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
def create_sitemap_df(**cfg):
    """[create the metadata of the sitemap]
    """    
    url, fp, nw = cfg['url'], cfg['dir'], cfg['NUM_WORKERS']
    if not os.path.exists(fp + '/'):
        os.mkdir(fp)
    xmls = _get_xmls(url)
    
    with Pool(nw) as p:
        df_list = list(tqdm(p.imap_unordered(_create_xml_df, xmls), total = len(xmls), position=0, leave=True))
    metadata = pd.concat(df_list, ignore_index=True)
    metadata.to_csv(fp + '/metadata.csv',index = False)
def _download_app(url, fp, app):
    """[download a apk file to the output path]
    Arguments:
        url {[string]} -- [url link of the file]
        op {[string]} -- [output file path]
    """'''    '''
    url += '/download?from=details'
    resp = requests.get(url)
    op = fp + '/raw/apps'
    apk_dir = op + '/' + app + '/' +app + '.apk'
    if not os.path.exists(op + '/' + app):
        os.mkdir(op + '/' + app)
    try:
        soup = bs4.BeautifulSoup(resp.text, 'html.parser')
        download_link = soup.find("iframe", {"id": "iframe_download"})['src']
        resp = requests.get(download_link)
        data = resp.content
        with open(apk_dir, 'wb') as fh:
            fh.write(data)
    except:
        return app, 'failed'
    return app, 'success'
def _decompose_app(fp, app, clean,verbose):
    """[decompose apk file]
    
    Arguments:
        app {[string]} -- [apk name]
        clean {[boolean]} -- [clean apk after decompose or not]
        verbose {[boolean]} -- [verbose the process or not]
    
    Returns:
        [string] -- [apk name]
    """    
    apk_dir = fp + '/' + 'raw' + '/' + 'apps' + '/' + app + '/' +app + '.apk'
    op = fp + '/raw/'+'/' + 'smali' + '/' + app
    if verbose:
        print('fetched {}, start decoding'.format(apk_dir))
        command = subprocess.run([
                'apktool', 'd', 
                apk_dir,
                '--no-res',
                '-o', op], capture_output = True)
        print(command.stdout.decode())
    else:
            command = subprocess.run([
                'apktool', 'd', 
                apk_dir,
                '-o', op])
    for i in glob(op + '/*'):
            if i not in glob(op + '/smali*'):
                try:
                    shutil.rmtree(i)
                except NotADirectoryError:
                    os.remove(i)
    if clean:
        os.remove(apk_dir)
    return app
def sampling(**cfg):
    """[sampling sitemap to get our data sample]
    Arguments:
        mode {[string]}: 
            "random" -- [random sample based]
            "group" -- [group sample based (Not inplemented)]
        size {[int]} -- [get how many samples]
        op {[string]} -- [output file directory]
        metadata_dir {[string]} -- [metadata file directory]
        fp {[string]} -- [app target download directory]
    """    
    mode, size, op, metadata_dir, fp = cfg['mode'], cfg['size'], cfg['op'], cfg['metadata_dir'], cfg['fp']
    metadata = pd.read_csv(metadata_dir)
    if mode == 'random':
        urls = metadata.sample(size)['loc'].tolist()
        app_url = {
            'dir': fp,
            'urls': urls,
            'verbose': True,
            'clean': True
        }
    with open(op, 'w') as f:
        json.dump(app_url, f)
def get_data(**cfg):
    """[download and extract the apks]
    Arguments:
        dir {[string]} -- [downloading directory]
        urls {[string]} -- [url link of the file]
        clean {[boolean]} -- [clean apk after decompose or not]
        verbose {[boolean]} -- [verbose the process or not]
    
    Returns:
        [string] -- [success message]
    """  
    fp, urls, verbose, clean, appmap = cfg['dir'], cfg['urls'], cfg["verbose"], cfg['clean'], cfg['appmap']
    if not os.path.exists(fp + '/'):
        os.mkdir(fp + '/')
    if not os.path.exists(fp + '/raw/'):
        os.mkdir(fp + '/raw/')
    if not os.path.exists(fp + '/raw/apps'):
        os.mkdir(fp + '/raw/apps')
    if not os.path.exists(fp + '/raw/smali'):
        os.mkdir(fp + '/raw/smali')
    if not os.path.exists(fp + '/interim/'):
        os.mkdir(fp + '/interim/')
    if not os.path.exists(fp + '/interim/appfeature'):
        os.mkdir(fp + '/interim/appfeature')
    if not os.path.exists(fp + '/interim/metadata'):
        os.mkdir(fp + '/interim/metadata')
    if not os.path.exists(fp + '/processed/'):
        os.mkdir(fp + '/processed')
    if not os.path.exists(fp + '/processed/matrix_A'):
        os.mkdir(fp + '/processed/matrix_A')
    client = Client()
    client.restart()
    NUM_WORKER = int(len(client.scheduler_info()['workers']))
    get_app_name = lambda url: re.findall(r'https:\/\/apkpure.com\/(.*?)\/', url)[0]
    downloading = [delayed(_download_app)(url, fp, get_app_name(url)) for url in urls]
    apps = {get_app_name(i):{'download':'', 'decode':''} for i in urls}
    for i in tqdm(range(0, len(downloading), NUM_WORKER)):
        proc_downloading = downloading[i: i + NUM_WORKER]
        app = dask.compute(proc_downloading)[0]
        for j in app:
            apps[j[0]]['download'] = j[1]
    extract_app = []
    for app in apps.keys():
        if apps[app]['download'] == 'failed':
            apps[app]['decode'] = 'failed'
        else:
            extract_app.append(app)
    extract_app = [delayed(_decompose_app)(fp, app, clean,verbose) for app in extract_app]
    for i in tqdm(range(0, len(extract_app), NUM_WORKER)):
        proc_extract_app = extract_app[i: i + NUM_WORKER]
        app = dask.compute(proc_extract_app)[0]
        for j in app:
            apps[j]['decode'] = 'done'
    app_map = appmap
    with open(app_map, 'w') as fp:
        json.dump(apps, fp)
    return 'apk download and decode finished'