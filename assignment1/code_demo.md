#### Data Sampling

  get the list of apks url to download from `sitemap.xml`

- [x] Initialize `metadata.csv` from `sitemap.xml`

    Initialize a metadata gives us a hint what data to sample:

- [x] Naive sampling
  
    random sample same amount of apks from APKPure to the malware sample.

    **usage**

    sampling 1000 benigned apks

    ```python
    import json
    sys.path.append('./utils')
    import utils
    import pandas as pd
    cfg = json.load(open('./sitemap.json'))
    utils.create_sitemap_df(**cfg) #Create a sitemap dataframe with corresponding info.
    metadata = pd.read_csv('./data/metadata/metadata.csv')
    metadata.sample(1000)
    urls = metadata.loc
    ```

- [ ] Category Sampling *will be inplement after feature extraction
  
  sampling same number of apks according to corresponding category from APKPure with the malware sample.

  First sample a smaller set from sitemap, then fetch the category of each apps by requesting apps' links. With each category get the even matched links to sample.

     **usage**

  ```python
  ###TODO
  ```

- [ ] Future Sample Methods Coming Soon...
  
  update after observation of first two sampling methods.
  
#### Data Downloading

- [x] Given a `app-url.json` to execute download.

    For example, to download `facebook` and `Plague Inc.` apps to `./data` directory the `app-url.json` may look like:

  ```json
  {
  "data_dir": "./data",
  "urls": [
      "https://apkpure.com/plague-inc/com.miniclip.plagueinc",
      "https://apkpure.com/instagram/com.instagram.android"
      ],
  "verbose": 1
  }
  ```

   **usage**

  ```python
  import json
  import re
  sys.path.append('./utils')
  import utils
  cfg = json.load(open('./demo/app-url.json'))
  urls, fp = cfg['urls'], cfg['data_dir']
  for url in urls:
    app = re.findall(r'https:\/\/apkpure.com\/(.*?)\/', url)[0]
    utils.download_app(url, fp, app)
  ```

#### Converting apks to smali

- [x] APK -> Smali using apktool

  check the documentation of [APKTool](https://ibotpeaches.github.io/Apktool/documentation/)

#### Fetching and Storing Data

The complete pipeline of getting both metadata and downloading apk and decompose them into data schemas.

[Demo Notebook](./demo/demo.ipynb)

- [x] fetching data consists downloading apk and decompose them into data schemas.

  **usage**

  ```python
  import json
  sys.path.append('./utils')
  import utils
  cfg = json.load(open('./demo/app-url.json'))
  utils.get_data(**cfg)
  >>> fetched ./data/plague-inc/plague-inc.apk, start decoding
  >>> I: Using Apktool 2.4.1 on plague-inc.apk
  >>> I: Loading resource table...
  >>> I: Decoding AndroidManifest.xml with resources...
  >>> I: Loading resource table from file: /Users/syeehyn/Library/apktool/framework/1.apk
  >>> I: Regular manifest package...
  >>> I: Decoding file-resources...
  >>> I: Decoding values */* XMLs...
  >>> I: Baksmaling classes.dex...
  >>> I: Copying assets and libs...
  >>> I: Copying unknown files...
  >>> I: Copying original files...

  fetched ./data/instagram/instagram.apk, start decoding
  >>> I: Using Apktool 2.4.1 on instagram.apk
  >>> I: Loading resource table...
  >>> I: Decoding AndroidManifest.xml with resources...
  >>> I: Loading resource table from file: /Users/syeehyn/Library/apktool/framework/1.apk
  >>> I: Regular manifest package...
  >>> I: Decoding file-resources...
  >>> I: Decoding values */* XMLs...
  >>> I: Baksmaling classes.dex...
  >>> I: Baksmaling classes2.dex...
  >>> I: Baksmaling classes3.dex...
  >>> I: Baksmaling classes4.dex...
  >>> I: Copying assets and libs...
  >>> I: Copying unknown files...
  >>> I: Copying original files...
  ```

- [x] fetching the sitemap DataFrame

  **usage**

  ```python
  import json
  sys.path.append('./utils')
  import utils
  utils.setup_env()
  cfg = json.load(open('./demo/sitemap.json'))
  utils.create_sitemap_df(**cfg)
  ```