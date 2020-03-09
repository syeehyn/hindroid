import requests
import bs4
import os
import shutil
def _download_app(url, fp, app):
    """[download a apk file to the output path]
    Arguments:
        url {[string]} -- [url link of the file]
        op {[string]} -- [output file path]
    """'''    '''
    url += '/download?from=details'
    resp = requests.get(url)
    op = os.path.join(fp, 'raw/apps')
    smali = os.path.join(fp, 'raw/smali')
    apk_dir = op + '/' + app + '/' +app + '.apk'
    smali_dir = smali +'/' + app
    if os.path.exists(smali_dir):
        return app, 'success'
    if not os.path.exists(op + '/' + app):
        try:
            os.mkdir(op + '/' + app)
        except:
            return app, 'failed'
    try:
        soup = bs4.BeautifulSoup(resp.text, 'html.parser')
        download_link = soup.find("iframe", {"id": "iframe_download"})['src']
        resp = requests.get(download_link)
        data = resp.content
        with open(apk_dir, 'wb') as fh:
            fh.write(data)
    except:
        try:
            shutil.rmtree(op + '/' + app)
            return app, 'failed'
        except:
            return app, 'failed'
    return app, 'success'