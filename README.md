# Hindroid

This repository contains a mimic implementation and future implementation plan of the [Hindroid](https://www.cse.ust.hk/~yqsong/papers/2017-KDD-HINDROID.pdf) paper (DO>>> I:[10.1145/3097983.3098026](https://doi.org/10.1145/3097983.3098026)).

Project|build Status
---|---
Data Ingesting| Success
Feature Extraction| Success
ML Deployment | Success

- Project Abstract
  - [Hindroid](#hindroid)
    - [What Is Hindroid](#what-is-hindroid)
- [Usage Instruction](#usage-instruction)
  - [Use run.py](#use-runpy)
  - [Use Library Code Directly](#use-library-code-directly)
- [Description of Contents](#description-of-contents)
  - [src](#src)
  - [config](#config)
  - [data](#data)
  - [Dockerfile](#dockerfile)
  - [notebooks](#notebooks)
- [Prerequisite](#prerequisite)
  - [Packages](#packages)
  - [Use Dockerfile](#use-dockerfile)
- [References](#references)

## What Is Hindroid

The main task of Hindroid is to use machine learning, typically Graph Neural Network, to classify Android Apps as benign or malicious. Hindroid is designed to be an intelligent Android malware detection system based on structured heterogeneous information network.

[Details](https://github.com/shy166/hindroid/blob/master/writeups/overview.md)

------------------------------------------------------------------------------------------------

## Usage Instruction

### Use `run.py`

#### Data Ingestion

Parameter Json

```json
{
"dir": "../data",
"urls": [
    "https://apkpure.com/plague-inc/com.miniclip.plagueinc",
    "https://apkpure.com/instagram/com.instagram.android",
    "https://apkpure.com/youtube/com.google.android.youtube",
    "https://apkpure.com/google-chrome-fast-secure/com.android.chrome",
    "https://apkpure.com/facebook/com.facebook.katana"
    ],
"appmap": "../data/raw/testmap.json",
"verbose": true,
"clean": true
}
```

- `dir`: the output directory of data ingestion.
- `urls`: the urls of apks to download.
- `appmap`: the app map file directory after data ingestion.
- `verbose`: verbose the process of data ingestion or not.
- `clean`: delete apk file after data ingestion or not.


```bash
#fetching data
python run.py data
```

#### Data Process

Parameter Json

```json
{
    "fp": "../data/raw/smali",
    "map_dir": "../data/raw/testmap.json",
    "op": "../data/interim/appfeature"
}
```

- `fp`: the file path of smali code.
- `map_dir`: the file path of app map.
- `op`: the output path of processed apps

------------------------------------------------------------------------------------------------

## Description of Contents

```
├── Dockerfile
├── LICENSE
├── README.md
├── config
│   ├── data-params.json
│   ├── env.json
│   ├── sample-params.json
│   ├── test-params.json
│   ├── test-sample.json
│   └── train-params.json
├── notebooks
│   └── EDA_Malware&Benign.ipynb
├── requirements.txt
├── run.py
├── src
│   ├── __init__.py
│   ├── datasets
│   │   ├── __init__.py
│   │   ├── fetching.py
│   │   └── sampling.py
│   ├── features
│   │   ├── __init__.py
│   │   ├── _extraction.py
│   │   └── features.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── _matrices.py
│   │   ├── baseline.py
│   │   ├── hindroid.py
│   │   └── utils.py
│   └── utils
│       ├── __init__.py
│       ├── _decompose.py
│       ├── _download.py
│       ├── _get_malware_dir.py
│       └── metadata.py
└── writeups
    └── overview.md
```

### `src`

- `utils.py`: Library code that executes tasks useful for getting data.
- `feature.py`: Library code that executes tasks useful for processing data.
- `matrices.py`: Library code that executes tasks useful for constructing matrices.
- `models.py`: Library code that executes tasks useful for training models.

### `config`

- `data-params.json`: common parameters for getting sampling data, serving as inputs to library code.
- `test-params.json`: parameters for getting small test data.

### `Dockerfile`

Contains the deployment of environment of this project

### `notebooks`


## Prerequisite

### Packages

The project is mainly built upon following packages:

- [ApkTool](https://ibotpeaches.github.io/Apktool/)

- [Pandas](https://pandas.pydata.org/)

- [Dask](https://dask.org/)

- [Spark](https://spark.apache.org/)

### Use Dockerfile

  You can build a docker image out of the provided [DockerFile](Dockerfile)

  ```bash
  $ docker build . # This will build using the same env as in a)
  ```

  Run a container, replacing the ID with the output of the previous command

  ```
  $ docker run -it -p 8888:8888 -p 8787:8787 <container_id_or_tag>
  ```
  
  The above command will give an URL (Like http://(container_id or 127.0.0.1):8888/?token=<sometoken>) which can be used to access the notebook from browser. You may need to replace the given hostname with "localhost" or "127.0.0.1".

## References

References are found both in the weekly readings, as well as in
[references](references.md). These will be update throughout the
quarter.

[HinDroid](https://www.cse.ust.hk/~yqsong/papers/2017-KDD-HINDROID.pdf)
paper on Malware detection.

- Malware Background

  - [Computer Viruses and
    Malware](https://www.springer.com/us/book/9780387302362) by Aycock,
    John. Available for pdf download on campus networks or VPN.

  - [Slides](http://cseweb.ucsd.edu/classes/sp18/cse127-a/CSE127sp18.18-Savage.pdf)
    for the Malware and Cybercrime lecture of CSE 127 at UCSD.

  - A [reference
    sheet](http://pages.cpsc.ucalgary.ca/~joel.reardon/mobile/smali-cheat.pdf)
    for decompiling Android applications to Smali Code.

- Graph Techniques in Machine Learning

  - A (graduate) [survey course](http://web.eecs.umich.edu/~dkoutra/courses/W18_598/) at Michigan on Graph Mining.

- Machine Learning on Source Code

  - A [collection](https://github.com/src-d/awesome-machine-learning-on-source-code)
  of papers and references exploring understanding source code with
  machine learning
