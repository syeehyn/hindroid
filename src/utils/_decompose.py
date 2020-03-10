import subprocess
from glob import glob
import shutil
import os
def _decompose_app(fp, app, clean,verbose):
    """[decompose apk file]
    
    Arguments:
        app {[string]} -- [apk name]
        clean {[boolean]} -- [clean apk after decompose or not]
        verbose {[boolean]} -- [verbose the process or not]
    
    Returns:
        [string] -- [apk name]
    """
    app_dir = os.path.join(fp, 'raw/apps/', app)
    apk_dir = os.path.join(fp, 'raw/apps/', app, '{}.apk'.format(app))
    op = os.path.join(fp, 'raw/smali/{}'.format(app))
    if os.path.exists(op):
        if clean:
            try:
                shutil.rmtree(app_dir)
            except FileNotFoundError:
                pass
            return app
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
                '-o', op], capture_output=True)
    for i in glob(op + '/*'):
            if i not in glob(op + '/smali*'):
                try:
                    shutil.rmtree(i)
                except NotADirectoryError:
                    os.remove(i)
    if clean:
        try:
            shutil.rmtree(app_dir)
        except:
            pass
    return app