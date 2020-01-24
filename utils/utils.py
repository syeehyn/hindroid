import os
import re
import subprocess
import glob
import requests
import bs4
import zlib
def decompose(fp, op, verbose = 0):
    """[decompose an apk file]
    
    Arguments:
        fp {[string]} -- [apk file path]
        op {[string} -- [output file path]
    
    Keyword Arguments:
        verbose {1/0} -- [verbose] (default: {0})
    """    
    fn = re.findall(r'[^\/\/]*(?=[.][a-zA-Z]+$)', fp)[0]
    if verbose:
        print('Start decomposing file: {}'.format(fn+'apk'))
        print('========================================================')
    subprocess.call(['apktool','d',fp,'-o', op+'/'+fn])
    if verbose:
        print('Decomposing finished')

def decompose_dir(fp, op, verbose = 0):
    """[decompose apk files from a directory]
    decompose_dir('/Users/syeehyn/Downloads/apk', '/Users/syeehyn/Downloads/apk/outputs')
    Arguments:
        fp {[string]} -- [apk file path]
        op {[string]} -- [output file path]
    
    Keyword Arguments:
        verbose {1/0} -- [verbose] (default: {0})
    """
    apks = glob.glob(fp+"/*.apk")
    for f in apks:
        decompose(f, op, verbose)
def download_apps(url, op):
    """[download apk from a given xml.gz link]
        url = "https://apkpure.com/sitemaps/group.xml.gz"
        path = "/Users/syeehyn/Downloads/apk"
        download_apps(url, path)
    Arguments:
        url {[string]} -- [xml.gz url]
        op {[string]} -- [output file path]
    """'''    '''
    response = requests.get(url, stream=True)
    f = response.raw.read()
    f = bytearray(f)
    urlText = zlib.decompress(f, 15+32)
    soup = bs4.BeautifulSoup(urlText, 'html.parser')
    app_links = soup.find_all('loc')
    print("approximate {} apk files to download".format(len(app_links)))
    counter = 0
    for links in app_links:
        download_link = get_app_urls(links.string)
        if download_link:
            download_app(download_link, op)
        counter += 1
        print('{0}/{1}'.format(counter, len(app_links)),end = '\r')
def get_app_urls(url):
    """[get download link of the app]
    
    Arguments:
        url {[string]} -- [url of the app page]
    
    Returns:
        [string] -- [download url of the app]
    """'''    '''
    response = requests.get(url)
    urlText = response.text
    soup = bs4.BeautifulSoup(urlText, 'html.parser')
    for i in soup.findAll("div", {"class": "down"}):
        if len(i.findAll("a", {"class" : ""})) != 0:
            return 'https://apkpure.com' + i.find("a", {"class" : ""})['href']


def download_app(url, op):
    """[download a apk file to the output path]
    
    Arguments:
        url {[string]} -- [url link of the file]
        op {[string]} -- [output file path]
    """'''    '''
    app = re.findall(r'https:\/\/apkpure.com\/(.*?)\/', url)[0] + '.apk'
    url += '/download?from=details'
    resp = requests.get(url)
    try:
        soup = bs4.BeautifulSoup(resp.text, 'html.parser')
        download_link = soup.find("iframe", {"id": "iframe_download"})['src']
        resp = requests.get(download_link)
        data = resp.content
        with open(op + '/' + app, 'wb') as fh:
            fh.write(data)
    except AttributeError:
        pass
def get_apks(**cfg):
    fp, urls = cfg['dir'], cfg['urls']
    if not os.path.exists(fp + '/'):
        os.mkdir(fp + '/')
    for url in urls:
        download_app(url, fp)