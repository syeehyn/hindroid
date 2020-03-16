# Hindroid

This repository contains a mimic implementation and future implementation plan of the [Hindroid](https://www.cse.ust.hk/~yqsong/papers/2017-KDD-HINDROID.pdf) paper (DO>>> I:[10.1145/3097983.3098026](https://doi.org/10.1145/3097983.3098026)).

## What Is Hindroid

The main task of Hindroid is to use machine learning, typically Graph Neural Network, to classify Android Apps as benign or malicious. Hindroid is designed to be an intelligent Android malware detection system based on structured heterogeneous information network.


## What is the Data

### APK and Smali

The paper uses a static analysis method to identify malware, extracting source code from [.apk](https://en.wikipedia.orwiki/Android_application_package) files of apps. Because of reversibility of .apk files, we will decompile .apk files to [Smali Code](https://limbenjamin.com/articles/analysing-smali-code.html) with  [ApkTool](https://ibotpeaches.github.io/Apktool/). We then use technique similar to Natural Language Processing to perform feature extraction outputting corresponding features, in particular, Nodes and Edges of the network.

The paper is mainly targeting on API calls in smali code. [API](https://en.wikipedia.org/wiki/Application_programming_interface), Application Programming Interfaces, is an interface or communication protocol between parts of a computer program intended to simplify the implementation and maintenance of software. API calls are used by Android apps in order to access operating system functionality and system resources. API calls grant possibility to apps access asking system permission to perform low level system actions like sending HTTP requests to an unknown server.

#### Example

API calls via Smali

```smali
invoke−virtual {v2, v3}, Ljava/lang/Runtime;−>exec(Ljava/lang/String ;)
Ljava / lang / Process ;
```

```smali
invoke−virtual {v2}, Ljava / lang / Process;−>getInputStream () Ljava / io / InputStream
```

### Data Design & Collection

#### Abstract

The data we use in replication of paper will consist of:

- Benign Android Application from [APKPure](http://apkpure.com)
- Malicious Android Application from our private source.

The benign apps are from an online app platform (like Playstore) APKPure. The reason we use APKPure instead of Google Playstore that APKPure is more scraping-friendly than Playstore: Playstore requires a google account to purchase free app. We can use sitemap of APKPure to sample our benign apps. More importantly, APKPure is an apk recommending site which consists app pre-census step by editors. It can reduce the possibility to get malicious app in our benign app samples.
The malicious Android Application are from our private source because of to avoid the data be used in malicious way.

With the Benign sample and the Malicious sample, we have both positive and negative labels in our classification task, then we will perform ML algorithms for binary classification.

While portions focused on learning graph techniques will also use
examples from other languages (for example, python and java source code).
Under folder utils, building utility functions to download apk and transfer apks smali code with python

#### Pros

- Using Smali as our data is appropriate with following reasons:
  - perform static analysis is a novel and secure way to perform malware detection. Rather than traditional detection on apks by running in a virtual machine or actual machine, it will not execute the apks. In this way, we can prevent the malware to actual damage our personal devices while we do malware detection.
  - perform static analysis is an efficient way to process large task when we want to perform a mass malware detection over apps, not only in personal use but also in business use. Rather than detecting the malware by running the file, we scan through the code.
  - perform static analysis is more robust with iteration. Iteration by feeding in new data and tuning parameter, the classification task will follow the trend of malware and detect them precisely.
- Using APKPure as our benign data is appropriate with following reasons:
  - APKPure is a secondary app store rather than Playstore, which has significantly less census on app release. Thus, APKPure's samples are more trust-worthy and can be good positive samples.
  - APKPure is scratching-friendly. Compared to Playstore, which requires a google account to download and purchase apps, APKPure does not require an accont to download apks. Moreover, APKPure provides a sitemap on the robots.txt. We can use the sitemap to easier sample our dataset.
- The benign Android Application and Malware samples are a good match to solve our classification task. As mentioned above, APKPure
  - With balanced of positive and negative samples of apk, we can build a robust classifier to identify malware and benign apps.

#### Cons

- Limitation of Benign Sample
  - Although APKPure is more trust-worthy than Google Playstore, it is still questionable that every app in APKPure is benign. If a large amount of our positive samples are negative, our classifier will be less robust even invalidated. We must aware the shortcoming that not every app in APKPure is benign.
  - Since we can only download free app from APKPure, there is a big limitation of our data design: we cannot access the paid apps, which is far away from our real world scenario. Despite the low malware possibility of paid apps, we cannot neglect the sample of paid apps.
- Limitation of Malicious Sample
  - The apps from APKPure is updated over time, but our malicious sample is from historical database. There is a time gap between our Benign sample and Malicious sample, and it is not easy to keep malicious sample updated.
  - The malicious sample is much less than the benign sample. It is not easy to make two sample balanced.
- Limitation of Only Detecting API calls
  - Our paper only targets on API calls, there exit malicious apps contain non-suspect API calls, which cannot be detected by our classifier. Also, the paper neglect to analysis the relationship between each method and class.
  - The repeat use of a specific API call will not feed in to the feature extraction of the paper, which will lead an inaccuracy of classifier.

#### Past Efforts

- Traditional Approach
  - The traditional approach of malware detection or security threats is to scan the signature of the apps compares to the database of identified malicious apps. This approach is harder to iterate because it requires to keep update the malware database.
- Dynamic Analysis
  - Others using dynamic analysis to perform malware detection. Because this method requires an active virtual machine to run the apps, it may have security concern and it is more computationally heavy.
- Static Analysis
  - Rather than extracting API calls using a structured heterogeneous information network, some constructed similarities between apps with ML to identify malware.

### Data Ingestion Process

#### Data Accessability

- Data Original
  - Benign Android Application from [APKPure](http://apkpure.com)
  - Malicious Android Application from our private source.
- Legal Issues
  - According to APKPure's [Term of Use](https://apkpure.com/terms.html)

    ```Note: APKPure.com is NOT associated or affiliated with Google, Google Play or Android in any way. Android is a trademark of Google Inc. All the apps & games are property and trademark of their respective developer or publisher and for HOME or PERSONAL use ONLY. Please be aware that APKPure.com ONLY SHARE THE ORIGINAL APK FILE FOR FREE APPS. ALL THE APK FILE IS THE SAME AS IN GOOGLE PLAY WITHOUT ANY CHEAT, UNLIMITED GOLD PATCH OR ANY OTHER MODIFICATIONS.```

    it specifies APKPure's data is only for personal use. Since our project is a personal capstone project without commercial purpose. We are free of legal Issues in data use.
  - According to APKPure's [robots.txt](https://apkpure.com/robots.txt), [sitemap.xml](https://apkpure.com/sitemap.xml) is obtained for scraping use. Thus, we are free of violation of scraping rule.

#### Data Privacy

*subject to change

- According to APKPure's [Privacy Policy](https://apkpure.com/privacy-policy.html). If necessary, we will provide our privacy information as policy requests.
- For data we collected, since it is public by APKPure, we are free of privacy concern. Regardlessly, we will still anonymise our data by following steps:
  - anonymise apk url with sha256 encryption.
  - anonymise app name with two-way hash function.
  - anonymise apk file names ,if necessary, with sha256 encryption.
  - anonymise apk developer with two-way hash function.
  - anonymise apk signature ,if necessary, with sha256 encryption.
  - anonymise apk category with two-way hash function.

#### Data Schemas

- Since we need to feed in data into a ML pipeline to make classification, we need preprocess our data, storing as a designed Data Schema like following form:

``` source
├── datasets
│   ├── external
│   ├── interim
│   │   ├── b_features
│   │   └── m_features
│   ├── processed
│   │   ├── matrices
│   │   │   ├── A.npz
│   │   │   ├── B.npz
│   │   │   ├── P.npz
│   │   │   └── ref
│   │   │       ├── api_ref.json
│   │   │       └── app_ref.json
│   │   └── results
│   │           └── results.csv
│   └── raw
│       ├── apps
│       └── smali
├── metadata
│   └── metadata.csv
└── tests
    ├── external
    ├── interim
    │   ├── b_features
    │   └── m_features
    ├── processed
    │   ├── matrices
    │   │   ├── A.npz
    │   │   ├── B.npz
    │   │   ├── P.npz
    │   │   └── ref
    │   │       ├── api_ref.json
    │   │       └── app_ref.json
    │   └── results
    │          └── results.csv
    └── raw
        ├── apps
        └── smali

```

  Since apks are fairly large, and we are interested in the API call of every app. We may only keep the file AndroidManifest.xml and smali folders. For each app, after extraction of smali, we will delete the .apk file

- For each app, we will create an overall metadata.csv to store their feature according their corresponding sitemap.

  The metadata will consist following columns:

  - `loc`: the url of specific app
  - `lastmod`: the datetime of the last update of the app
  - `changefreq`: check for update frequency
  - `priority`: the priority group of the app
  - `sitemap_url`: the url in sitemap.xml

  Metadata is a map of what we will sample according to, we can do different sampling with the metadata.

### Data Ingestion Pipeline

#### Data Sampling

  get the list of apks url to download from `sitemap.xml`

- Initialize `metadata.csv` from `sitemap.xml`

    Initialize a metadata gives us a hint what data to sample:

- Naive sampling
  
    random sample same amount of apks from APKPure to the malware sample.
  
#### Data Ingesting

- Given a `app-url.json` to execute download.
- APK -> Smali using apktool

## Feature Extraction

### API Call Extraction

  Each app's samli code will be extracted into api calls and be grouped into .csv file. For example, instagram's smali code will be extracted as `instagram.csv` with following columns: `block`, `invocation`, `package`, `method_name`, `app`.

- Extract API Calls of Apps: `package` + '->' + `method_name`
- Extract method name of API Calls: `method_name`
- Extract Code blocks of API Calls: `block`
- Extract Package used of each API Calls: `package`
- Extract Invocation of each API Calls: `invocation`

## EDA and Sampling
in the end of the report

## ML Deployment

### Baseline Model

- The baseline mode lies under directory `src/models/baseline.py`

- It uses the results from EDA to build on following features engineering pipelin upon each app:

#### 1. Preprocess

    - numerical:
        - `api`: number of unique apis
        
        - `block`: number of unique blocks
        
        - `package`: number of packages
        
    - categorical:
    
        
        - `most_api`: the most called api
        
        - `package`: the most used package
        
#### 2. Column Transfer:

    - the column transfere process follows following rule based on data type:
    
        - `numerical`: Standardized by Scikit Learn Standard Scaler
        
        - `catogorical`: Transferred to dummy variable by Scikit Learn OneHot Encoder
        
#### 3. Classifier:

    - Logistic Regression
    
    - SVM
    
    - Random Forest

    The performance and result showed below

#### 4. Results:

    for our 40 datasets sample, the metrics result after 10 iterations with .33 test size


    training metrics: 
                                  f1       acc    tp   fp    tn   fn
    method                                                          
    LogisticRegression      0.937315  0.930769  13.5  1.8  10.7  0.0
    RandomForestClassifier  0.992848  0.992308  13.5  0.2  12.3  0.0
    SVC                     0.931130  0.923077  13.5  2.0  10.5  0.0
    testing metrics: 
                                  f1       acc   tp   fp   tn   fn
    method                                                        
    LogisticRegression      0.864009  0.857143  6.5  2.0  5.5  0.0
    RandomForestClassifier  0.869842  0.864286  6.5  1.9  5.6  0.0
    SVC                     0.864009  0.857143  6.5  2.0  5.5  0.0


    for our 810 datasets sample, the metrics result after 10 iterations with .33 test size


    training metrics: 
                                  f1       acc     tp    fp     tn    fn
    method                                                              
    LogisticRegression      0.772912  0.796863  188.6  31.2  243.3  78.9
    RandomForestClassifier  0.988095  0.988376  262.5   1.3  273.2   5.0
    SVC                     0.698019  0.687085  196.1  98.2  176.3  71.4
    testing metrics: 
                                  f1       acc     tp    fp     tn    fn
    method                                                              
    LogisticRegression      0.730617  0.744403   93.3  24.3  106.2  44.2
    RandomForestClassifier  0.867058  0.866045  117.3  15.7  114.8  20.2
    SVC                     0.704158  0.684328  100.8  47.9   82.6  36.7


##### Observations

- The baseline model has a very decent result on small dataset. Since we do not have many dataset, it will avoid some overfitting in some cases.

- As the data set getting larger and larger, the baseline model works poorly. But for Random Forest, the model is still very robust because of the advantage of tree structured classifier.

### Hindroid Model

#### 1. Preprocess w/ Matrix Construction

  we used Hindroid's method to construct our feature matrix, the description as follows:

##### A Matrix

  $a_{ij}$ is defined as:
  
  "If $app_i$ contains $api_j$ , then $a_{ij} = 1$; otherwise, $a_{ij} = 0$."
  
###### implementation Detail
- using spark to create an adjacency matrix by first assigning every unique api calls and app with ids using `stringIndexer`, then output the unique pair of api id and app id and feeding into the sparse coordinate matrix to construct APP x API A Matrix
        
##### B Matrix
  
  $b_{ij}$ is defined as:
  
  "If $api_i$ and $api_j$ co-exist in the same code block, then $b_{ij}$ = 1; otherwise, $b_{ij}$ = 0."

###### implementation Detail
- Using the same approach of A to construct an API x Block matrix.
- Taking the dot product of (API x Block) and (Block x API) matrix to get an squared matrix, then filtering every non-negative term to 1, Then we have API x API B Matrix

##### P Matrix

  $p_{ij}$ is defined as:
  
  "If $api_i$ and $api_j$ are with the same package name, then $p_{ij}$ = 1; otherwise, $p_{ij}$ = 0."
  
###### implementation Detail

- Similiar to B matrix, first generating API x Package matrix and then take dot product and filtering.

#### 2. Fit into Precomputed Kernel SVM

- With the Matrices, we can make classifiers based on different Kernel Path. In specific, we have AA^T, ABA^T, APA^T, and APBP^TA^T implemented as kernel function of SVM. We used scikit learn built SVC to make our classifier. (sklearn.svm.SVC(kernel = 'precomputed').

#### 3. Why Hindroid ?

- hindroid is a very intuitive and reasonable approach. From our EDA, we can see a significant difference between Malware and Benign apps with api calls, packages, and blocks. Api calls mainly represent that malware may frequently call some api call, and there are some frequently used package with malwares. Also, the code blocks are good representations of complexity of apps since malware are less complext than benign apps in general.
- hindroid model utilizes those characters of API calls, code blocks, and packages to calculate the similarities between apps by constructing a Heterogeneous Information Network. In specific, AA^T means how many APIs are in common with a pair of apps. APA^T means how many pairs of APIs that uses a common package. ABA^T implies that two apps both called these specific APIs within a block in the code. With the intuitation, we can classify the apps with SVM kernel to make a decision boundary between benign apps and malware apps.

#### 4. Explaination of Implementation

- Since there are many and many different api calls, package, blocks in every app, we need to handle the data when it comes large. We are limited with memory, then distributed computing packages rather than pandas are brought to table: Spark and Dask. In specific, we used dask to handle the task stream of extracting api calls, blocks, etc from smali files, and we used pyspark to do matrix construction since Spark can easily handle the case of adjancency matrix.

- For B and P matrix, we first computted the API x Block matrix and API x Package matrix to reduce the computational cost. And then, we replaced the non-zero terms with 1. In this way, since there are large set of different api calls in our dataset, the number of unique block and number of package is much smaller.

- To store the matrices, we stored the adjacency matrices in Coordinate format `scipy.sparse.coo_matrix`. For matrix calculation, we simply uses its built-in dot product in scipy. i.e A.dot(B) We store our matrices by the file name `A.npz`, `P.npz`, `B.npz` with a reference folder `ref` containing `api_ref.json` and `app_ref.json` with mapping of which index of the matrix has which values.

- For SVM, we built own classifier class `hindroid` (in `src.models.hindroid`) with `scikit-learn SVC('precomputed')`

#### 5. Experimental Results

    for our 40 datasets sample, the metrics result after 10 iteration with .33 test size



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>f1</th>
      <th>acc</th>
      <th>tp</th>
      <th>fp</th>
      <th>tn</th>
      <th>fn</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1.0</td>
      <td>1.0</td>
      <td>12.8</td>
      <td>0.0</td>
      <td>13.2</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1.0</td>
      <td>1.0</td>
      <td>12.8</td>
      <td>0.0</td>
      <td>13.2</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1.0</td>
      <td>1.0</td>
      <td>12.8</td>
      <td>0.0</td>
      <td>13.2</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1.0</td>
      <td>1.0</td>
      <td>12.8</td>
      <td>0.0</td>
      <td>13.2</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
</div>



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>f1</th>
      <th>acc</th>
      <th>tp</th>
      <th>fp</th>
      <th>tn</th>
      <th>fn</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.876458</td>
      <td>0.857143</td>
      <td>7.2</td>
      <td>2.0</td>
      <td>4.8</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.874278</td>
      <td>0.857143</td>
      <td>7.1</td>
      <td>1.9</td>
      <td>4.9</td>
      <td>0.1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0.872079</td>
      <td>0.857143</td>
      <td>7.1</td>
      <td>1.9</td>
      <td>4.9</td>
      <td>0.1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0.860391</td>
      <td>0.835714</td>
      <td>7.0</td>
      <td>2.1</td>
      <td>4.7</td>
      <td>0.2</td>
    </tr>
  </tbody>
</table>
</div>


    for our 810 datasets sample, the metrics result after 810 iteration with .33 test size



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>method</th>
      <th>f1</th>
      <th>acc</th>
      <th>tp</th>
      <th>fp</th>
      <th>tn</th>
      <th>fn</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>AA</td>
      <td>1.000000</td>
      <td>1.000000</td>
      <td>268.3</td>
      <td>0.0</td>
      <td>273.7</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>ABA</td>
      <td>0.798013</td>
      <td>0.800185</td>
      <td>214.1</td>
      <td>54.1</td>
      <td>219.6</td>
      <td>54.2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>APA</td>
      <td>1.000000</td>
      <td>1.000000</td>
      <td>268.3</td>
      <td>0.0</td>
      <td>273.7</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>APBPA</td>
      <td>0.847698</td>
      <td>0.848155</td>
      <td>229.1</td>
      <td>43.1</td>
      <td>230.6</td>
      <td>39.2</td>
    </tr>
  </tbody>
</table>
</div>



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>method</th>
      <th>f1</th>
      <th>acc</th>
      <th>tp</th>
      <th>fp</th>
      <th>tn</th>
      <th>fn</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>AA</td>
      <td>0.962199</td>
      <td>0.961940</td>
      <td>129.9</td>
      <td>3.4</td>
      <td>127.9</td>
      <td>6.8</td>
    </tr>
    <tr>
      <th>1</th>
      <td>ABA</td>
      <td>0.775401</td>
      <td>0.773134</td>
      <td>105.5</td>
      <td>29.6</td>
      <td>101.7</td>
      <td>31.2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>APA</td>
      <td>0.936985</td>
      <td>0.935448</td>
      <td>128.1</td>
      <td>8.7</td>
      <td>122.6</td>
      <td>8.6</td>
    </tr>
    <tr>
      <th>3</th>
      <td>APBPA</td>
      <td>0.776825</td>
      <td>0.770522</td>
      <td>107.0</td>
      <td>31.8</td>
      <td>99.5</td>
      <td>29.7</td>
    </tr>
  </tbody>
</table>
</div>


###### Design
- We should use F beta score since our goal is to detect Malware, we want a more strict metrics than accuracy for different Precision and Recall demanding. In specific, if user want to be aware of more malwares, then the metrics should be more in favor of Recall: F beta > 1. If user thinks himself or herself will not be easily get malware apps, the metrics should be more in favor of Precision: F beta < 1
- In our report, we try to make the same result to compare with Hindroid paper, so we made the table above. F1 score meant to have a balanced between Recall and Precision.

###### Observation

- We notice that the performance will not be higher when the kernal path gets more complicates. That is, a simple AA^T matrix may outperformance every other meta path like APBP^TA^T. Since our benign set is balanced with malware set (same number of targets and same apk in size), our dataset is far away from real datasets. In our cases, the naive AA^T works the best for the fully balanced datasets.

- The Hindroid approach matches to hindroid paper results except for the methods involves B matrices. In this case, we suggest that the B matrix adds some noise on the Kernel matrix when training since our data set only consists the feature csv files with less than 5MB. We suggest that as the apk files being smaller, the weights of B will be getting larger, and then the noise of Block will impact the overall performance. We assume that with larger apk files trained into model, the weights of noise of B will be smaller, then the performance will get better. In other words, we make hypothesis that B matrix will benifit the model as apk files as training set getting larger and larger.

## Conclusion & Discussion

### Data Ingestion Pipeline

- For data downloading, we can download 2000+ apk in 5 minutes on DSMLP by taking advantage of parallelism in dask.
- For apk file decompiling, it took us nearly 10 hours to ingest those apk files to smali code. We question our techniques with following two points:
    - The `I/O cost` in DSMLP, in downloading process, it downloads files very fast and stores in the disk. The APK tool is designed to decompile apks one by one, and it only support decompile apk in disk. When we are using DSMLP, the decompiling time would be doubled than we decompile on SSD-driven laptop. So the I/O cost comes a big issue if we want to process large amount of training data of smalis.
    - The poor `parallelism implemented in dask` when dealing with python subprocess. We used dask to manage the parallelism because of its higher level task management and pandas-like API. It may work poorly when we parallel task in python subprocess.

### Feature Extraction

- For feature extraction, we also used pandas to extract each file with reading smali code files, and we used dask to parallel our tasks. For feature extraction of 2000+ apk, the total task took 5 hours. The tasks are expensive when we need larger datasets. We also question our techniques with `I/O cost` and `paralleim implemented in dask` mentioned in Data Ingestion Pipeline.

### Model Metrics Performance

- Compared to the basedline model which utlizes the statistical meaning of each features, the hindroid approach is more reliable when dataset comes larger in general. From our experimental results of hindroid, we have some unsolved question and hypothesis: `how the results will be as variety data trained into model`. 
- In specific, `how the will P and B impact the classfication as variety datasets trained in`. In the original paper of Hindroid, the ABA^T and AA^T outperforms all other metapath. In our results,AA^T also outperform others, but ABA^T performs even worse than our Random Forest in baseline model. We made the hypothesis that `B matrix works as a droupout layer to serve as a regularor to penalize over-fitting` since there exists a sign of over-fitting in AA^T meta path. To confirm such assumption, we need to ingest more dataset and see the training results.

### Model Computational Efficiency

- In `training` process, the Basedline and Hindroid models both uses `spark` to preprocess data and constructing matrix. The training process is surprisingly fast when we have 40 samples, the training process of both of them takes a few seconds (a few minutes in pure pandas). With 810 samples, the training process of both of them takes a few minutes (a few hours in pure pandas with memory concern). Also, more importantly, the memory usage is very low. We suggest that even in I matrix (not implemented), our approach will still solid and good.
- In `validation` and `testing`, we did our approaches in pure scikit-learn pipeline with no joblib parameters (no parallelism and distributed computing). For validation and testing over 40 samples, the baseline model takes a few seconds and hindroid model takes about 20+ seconds . For validation and testing over 810 samples, the baseline model takes about two minutes and the hindroid model takes about five minutes.

### Concern and Future

As right now, we have a full scope about how a project is been constructed, and we did several times roll-back in my development. i.e. we first constructed my training model process in dask, and it tooks forever to train, and then we switched to pyspark. Also, we still were still fixing our data ingestion pipeline when we were in training process, etc. We are sure that roll-back cases will still happen in future deployment of next project, but we want to avoid them as many as possible. We have following improvement and concern in future implementation: 

- data ingestion pipeline:
    - `I/O cost`, to reduce the I/O cost, we can get the source code of API Tool and twist it into an In-memory decompile tool to make the data ingestion pipleline faster.
    - `Parallelism`. We may think about switching to command-line own parallalim or other distributed computing library.
- feature extraction:
    - `I/O cost`, to reduce the I/O cost, we can integrate the feature extraction process in data ingetstion pipeline to do in-memory computing.
    - `Parallelism`. Using `spark` to do dataframe/tabular operation.
- model metrics performance:

    - `Classifier` the paper uses SVM to classify the preprocessed matrices, we can change differernt estimator to try out the results. i.e. We can use some tree-based algorithm like XGBoost to see if the performance will be better.
- model computational efficiency:

    - `Training`: Since the computational efficiency for training process is fairly good after switch to spark, we do not have any concern about it so far.
    
    - `Testing and Validation`: we can also switch our training, validation pipeline into the spark by using packages under spark.mlib. We can make the whole training and testing pipline in Spark.
    
    - `In general`, our implementation tried our best to optimize the process of preprocessing and training by trying different toolkit like Dask, Spark, etc. Downcasting the issue to basic level, the computation is trivial because of large number of unique api calls, packages, and blocks. I encountered different type of memory outrage when I implemented the model. There are different approaches suggested to fix the issue:
    
        - `Trim Down API Calls`, Like pruning a decision tree, trimming the API calls to fixed dictionary, the computational problem of API calls can be solved. It can also prevent the problem of overfitting.
        - `Change Embedding Method`, we can use more highly optimized graph technique to process the algorithm.

## Reference

This page contains references on topics covered in this domain of
inquiry and sometimes serves as a reference to the weekly reading,
sometimes as a supplement to materials covered in the course.

The main paper being replicated in this domain is the
[HinDroid](https://www.cse.ust.hk/~yqsong/papers/2017-KDD-HINDROID.pdf)
paper on Malware detection.

### Malware Background

* [Computer Viruses and
  Malware](https://www.springer.com/us/book/9780387302362) by Aycock,
  John. Available for pdf download on campus networks or VPN.
  
* [Slides](http://cseweb.ucsd.edu/classes/sp18/cse127-a/CSE127sp18.18-Savage.pdf)
  for the Malware and Cybercrime lecture of CSE 127 at UCSD.
  
* A [reference
  sheet](http://pages.cpsc.ucalgary.ca/~joel.reardon/mobile/smali-cheat.pdf)
  for decompiling Android applications to Smali Code.

### Graph Techniques in Machine Learning

* A (graduate) [survey course](http://web.eecs.umich.edu/~dkoutra/courses/W18_598/) at Michigan on Graph Mining.

### Machine Learning on Source Code

* A
  [collection](https://github.com/src-d/awesome-machine-learning-on-source-code)
  of papers and references exploring understanding source code with
  machine learning.

