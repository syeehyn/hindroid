import os
import re
import subprocess
import glob
import requests
import bs4
import zlib

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
    fp, urls = cfg['dir'], cfg['urls']
    if not os.path.exists(fp + '/'):
        os.mkdir(fp + '/')
    for url in urls:
        app = re.findall(r'https:\/\/apkpure.com\/(.*?)\/', url)[0]
        download_app(url, fp, app)
        