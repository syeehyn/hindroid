# Hindroid: An Android malware detection in Machine Learning

date: March 20, 2020
slug: Hindroid
status: Published
summary: An Android malware detection project based on the https://www.cse.ust.hk/~yqsong/papers/2017-KDD-HINDROID.pdf paper.
Hindroid uses machine learning, typically Graph Neural Network, to classify Android Apps as benign or malicious. Hindroid is designed to be an intelligent Android malware detection system based on structured heterogeneous information network. The project contains a comprehensive report and an in-depth evaluation of Hindroid model.
tags: Data Science, Graph Neural Network, Natural Language Processing, Project
type: Post

## What Is Hindroid

The main task of Hindroid is to use machine learning, typically Graph Neural Network, to classify Android Apps as benign or malicious. Hindroid is designed to be an intelligent Android malware detection system based on a structured heterogeneous information network.

## What is the Data

### APK and Smali

The paper uses a static analysis method to identify malware, extracting source code from [.apk](https://en.wikipedia.orwiki/Android_application_package) files of apps. Because of the reversibility of .apk files, we will decompile .apk files to [Smali Code](https://limbenjamin.com/articles/analysing-smali-code.html) with [ApkTool](https://ibotpeaches.github.io/Apktool/). We then use a technique similar to Natural Language Processing to perform feature extraction outputting corresponding features, in particular, Nodes and Edges of the network.

The paper is mainly targeting API calls in smali code. [API](https://en.wikipedia.org/wiki/Application_programming_interface), Application Programming Interfaces, is an interface or communication protocol between parts of a computer program intended to simplify the implementation and maintenance of software. API calls are used by Android apps in order to access operating system functionality and system resources. API calls grant possibility to apps access asking system permission to perform low-level system actions like sending HTTP requests to an unknown server.

### Example

API calls via Smali

```
invoke−virtual {v2, v3}, Ljava/lang/Runtime;−>exec(Ljava/lang/String ;)
Ljava / lang / Process ;
```

```
invoke−virtual {v2}, Ljava / lang / Process;−>getInputStream () Ljava / io / InputStream
```

### Data Design & Collection

### Abstract

The data we use in replication of paper will consist of:

- Benign Android Application from [APKPure](http://apkpure.com/)
- Malicious Android Application from our private source.

The benign apps are from an online app platform (like Playstore) APKPure. The reason we use APKPure instead of Google Playstore is that APKPure is more scraping-friendly than Playstore: Playstore requires a google account to purchase the free app. We can use a sitemap of APKPure to sample our benign apps. More importantly, APKPure is an apk recommending site that consists of app pre-census steps by editors. It can reduce the possibility to get the malicious apps in our benign app samples. The malicious Android Application is from our private source to avoid the data be used in a malicious way.

With the Benign sample and the Malicious sample, we have both positive and negative labels in our classification task, then we will perform ML algorithms for binary classification.

While portions focused on learning graph techniques will also use examples from other languages (for example, python and java source code). Under folder utils, building utility functions to download apk and transfer apks smali code with python

### Pros

- Using Small as our data is appropriate with following reasons:
    - perform the static analysis is a novel and secure way to perform malware detection. Rather than traditional detection on apks by running in a virtual machine or actual machine, it will not execute the apks. In this way, we can prevent the malware from actually damage our personal devices while we do malware detection.
    - perform the static analysis is an efficient way to process large tasks when we want to perform mass malware detection over apps, not only in personal use but also in business use. Rather than detecting the malware by running the file, we scan through the code.
    - perform the static analysis is more robust with iteration. Iteration by feeding in new data and tuning parameters, the classification task will follow the trend of malware and detect them precisely.
- Using APKPure as our benign data is appropriate with following reasons:
    - APKPure is a secondary app store rather than Playstore, which has significantly less census on app release. Thus, APKPure’s samples are more trustworthy and can be good positive samples.
    - APKPure is scratching-friendly. Compared to Playstore, which requires a google account to download and purchase apps, APKPure does not require an account to download apks. Moreover, APKPure provides a sitemap on the robots.txt. We can use the sitemap to easier sample our dataset.
- The benign Android Application and Malware samples are a good match to solve our classification task. As mentioned above, APKPure
    - With a balanced of positive and negative samples of apk, we can build a robust classifier to identify malware and benign apps.

### Cons

- Limitation of Benign Sample
    - Although APKPure is more trustworthy than Google Playstore, it is still questionable that every app in APKPure is benign. If a large number of our positive samples are negative, our classifier will be less robust even invalidated. We must aware of the shortcoming that not every app in APKPure is benign.
    - Since we can only download the free app from APKPure, there is a big limitation of our data design: we cannot access the paid apps, which is far away from our real-world scenario. Despite the low malware possibility of paid apps, we cannot neglect the sample of paid apps.
- Limitation of Malicious Sample
    - The apps from APKPure are updated over time, but our malicious sample is from a historical database. There is a time gap between our Benign sample and the Malicious sample, and it is not easy to keep the malicious sample updated.
    - The malicious sample is much less than the benign sample. It is not easy to make two samples balanced.
- Limitation of Only Detecting API calls
    - Our paper only targets API calls, their exit malicious apps contain non-suspect API calls, which cannot be detected by our classifier. Also, the paper neglect to analyze the relationship between each method and class.
    - The repeated use of a specific API call will not feed into the feature extraction of the paper, which will lead to an inaccuracy of the classifier.

### Past Efforts

- Traditional Approach
    - The traditional approach of malware detection or security threats is to scan the signature of the apps compares to the database of identified malicious apps. This approach is harder to iterate because it requires to keep update the malware database.
- Dynamic Analysis
    - Others using dynamic analysis to perform malware detection. Because this method requires an active virtual machine to run the apps, it may have security concern and it is more computationally heavy.
- Static Analysis
    - Rather than extracting API calls using a structured heterogeneous information network, some constructed similarities between apps with ML to identify malware.

### Data Ingestion Process

### Data Accessibility

- Data Original
    - Benign Android Application from [APKPure](http://apkpure.com/)
    - Malicious Android Application from our private source.
- Legal Issues
    - According to APKPure’s [Term of Use](https://apkpure.com/terms.html)
    it specifies APKPure’s data is only for personal use. Since our project is a personal capstone project without a commercial purpose. We are free of legal Issues in data use.

        `Note: APKPure.com is NOT associated or affiliated with Google, Google Play or Android in any way. Android is a trademark of Google Inc. All the apps & games are property and trademark of their respective developer or publisher and for HOME or PERSONAL use ONLY. Please be aware that APKPure.com ONLY SHARE THE ORIGINAL APK FILE FOR FREE APPS. ALL THE APK FILE IS THE SAME AS IN GOOGLE PLAY WITHOUT ANY CHEAT, UNLIMITED GOLD PATCH OR ANY OTHER MODIFICATIONS.`

    - According to APKPure’s [robots.txt](https://apkpure.com/robots.txt), [sitemap.xml](https://apkpure.com/sitemap.xml) is obtained for scraping use. Thus, we are free of violation of the scraping rule.

### Data Privacy

- subject to change
- According to APKPure’s [Privacy Policy](https://apkpure.com/privacy-policy.html). If necessary, we will provide our privacy information as policy requests.
- For the data we collected, since it is public by APKPure, we are free of privacy concerns. Regardlessly, we will still anonymize our data by following steps:
    - anonymize apk URL with sha256 encryption.
    - anonymize app name with a two-way hash function.
    - anonymize apk file names,if necessary, with sha256 encryption.
    - anonymize apk developer with a two-way hash function.
    - anonymize apk signature,if necessary, with sha256 encryption.
    - anonymize apk category with a two-way hash function.

### Data Schemas

- Since we need to feed in data into an ML pipeline to make classification, we need to preprocess our data, storing it as a designed Data Schema like the following form:

```
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

- For each app, we will create an overall metadata.csv to store their feature according to their corresponding sitemap.

    The metadata will consist following columns:

    - `loc`: the url of a specific app
    - `lastmod`: the DateTime of the last update of the app
    - `changefreq`: check for update frequency
    - `priority`: the priority group of the app
    - `sitemap_url`: the URL in sitemap.xml

    Metadata is a map of what we will sample according to, we can do different sampling with the metadata.

### Data Ingestion Pipeline

### Data Sampling

get the list of apks URL to download from `sitemap.xml`

- Initialize `metadata.csv` from `sitemap.xml`

    Initialize metadata gives us a hint of what data to sample:

- Naive sampling

    random sample same amount of apks from APKPure to the malware sample.

### Data Ingesting

- Given an `app-url.json` to execute download.
- APK -> Smali using apktool

## Feature Extraction

### API Call Extraction

Each app’s samli code will be extracted into API calls and be grouped into a .csv file. For example, Instagram's smali code will be extracted as `instagram.csv` with the following columns: `block`, `invocation`, `package`, `method_name`, `app`.

- Extract API Calls of Apps: `package` + ‘->’ + `method_name`
- Extract method name of API Calls: `method_name`
- Extract Code blocks of API Calls: `block`
- Extract Package used for each API Calls: `package`
- Extract Invocation of each API Calls: `invocation`

## EDA and Sampling

in the end of the report

## ML Deployment

### Baseline Model

- The baseline model lies under directory `src/models/baseline.py`
- It uses the results from EDA to build on the following features of engineering pipeline upon each app:

### 1. Preprocess

```
- numerical:
    - `api`: number of unique apis

    - `block`: number of unique blocks

    - `package`: number of packages

- categorical:

    - `most_api`: the most called api

    - `package`: the most used package

```

### 2. Column Transfer:

```
- the column transfer process follows the following rule based on data type:

    - `numerical`: Standardized by Scikit Learn Standard Scaler

    - `catogorical`: Transferred to dummy variable by Scikit Learn OneHot Encoder

```

### 3. Classifier:

```
- Logistic Regression

- SVM

- Random Forest

The performance and result showed below
```

### 4. Results:

```
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
```

### Observations

- The baseline model has a very decent result on a small dataset. Since we do not have many datasets, it will avoid some overfitting in some cases.
- As the data set getting larger and larger, the baseline model works poorly. But for Random Forest, the model is still very robust because of the advantage of the tree-structured classifier.

### Hindroid Model

### 1. Preprocess w/ Matrix Construction

we used Hindroid’s method to construct our feature matrix, the description is as follows:

### A Matrix

*aij* is defined as:

“If *appi* contains *apij* , then *aij* = 1; otherwise, *aij* = 0.”

### implementation Detail

- using spark to create an adjacency matrix by first assigning every unique API call and app with ids using `stringIndexer`, then output the unique pair of API id and app id and feeding into the sparse coordinate matrix to construct APP x API A Matrix

### B Matrix

*bij* is defined as:

“If *apii* and *apij* co-exist in the same code block, then *bij* = 1; otherwise, *bij* = 0.”

### implementation Detail

- Using the same approach of A to construct an API x Block matrix.
- Taking the dot product of (API x Block) and (Block x API) matrix to get a squared matrix, then filtering every non-negative term to 1, Then we have API x API B Matrix

### P Matrix

*pij* is defined as:

“If *apii* and *apij* are with the same package name, then *pij* = 1; otherwise, *pij* = 0.”

### implementation Detail

- Similar to B matrix, first generating API x Package matrix and then take dot product and filtering.

### 2. Fit into Precomputed Kernel SVM

- With the Matrices, we can make classifiers based on different Kernel Paths. In specific, we have AA^T, ABA^T, APA^T, and APBPT implemented as kernel functions of SVM. We used scikit learn to build SVC to make our classifier. (sklearn.svm.SVC(kernel = ‘precomputed’).

    TA

### 3. Why Hindroid ?

- hindroid is a very intuitive and reasonable approach. From our EDA, we can see a significant difference between Malware and Benign apps with API calls, packages, and blocks. Api calls mainly represent that malware may frequently call some API call, and there is some frequently used package with malware. Also, the code blocks are good representations of the complexity of apps since malware is less complex than benign apps in general.
- hindroid model utilizes those characters of API calls, code blocks, and packages to calculate the similarities between apps by constructing a Heterogeneous Information Network. In specific, AA^T means how many APIs are in common with a pair of apps. APA^T means how many pairs of APIs use a common package. ABA^T implies that two apps both called these specific APIs within a block in the code. With intuition, we can classify the apps with SVM kernel to make a decision boundary between benign apps and malware apps.

### 4. Explanation of Implementation

- Since there are many and many different API calls, packages, blocks in every app, we need to handle the data when it comes large. We are limited with memory, then distributed computing packages rather than pandas are brought to the table: Spark and Dask. In specific, we used dask to handle the task stream of extracting api calls, blocks, etc from smali files, and we used pyspark to do matrix construction since Spark can easily handle the case of the adjacency matrix.
- For B and P matrix, we first computed the API x Block matrix and API x Package matrix to reduce the computational cost. And then, we replaced the non-zero terms with 1. In this way, since there are a large set of different API calls in our dataset, the number of unique blocks and the number of packages is much smaller.
- To store the matrices, we stored the adjacency matrices in Coordinate format `scipy.sparse.coo_matrix`. For matrix calculation, we simply use its built-in dot product in scipy. i.e A.dot(B) We store our matrices by the file name `A.npz`, `P.npz`, `B.npz` with a reference folder `ref` containing `api_ref.json` and `app_ref.json` with mapping of which index of the matrix has which values.
- For SVM, we built own classifier class `hindroid` (in `src.models.hindroid`) with `scikit-learn SVC('precomputed')`

### 5. Experimental Results

```
for our 40 datasets sample, the metrics result after 10 iterations with .33 test size
```

[40 samples](https://www.notion.so/ba8bbe1270e04ae7b7c02e6268ab7275)

for our 810 datasets sample, the metrics result after 810 iteration with .33 test size

[810 samples](https://www.notion.so/cf86774076eb4379b9e64eb4ad048cd0)

### Design

- We should use F beta score since our goal is to detect Malware, we want a more strict metrics than accuracy for different Precision and Recall demanding. In specific, if user want to be aware of more malwares, then the metrics should be more in favor of Recall: F beta > 1. If user thinks himself or herself will not be easily get malware apps, the metrics should be more in favor of Precision: F beta < 1
- In our report, we try to make the same result to compare with Hindroid paper, so we made the table above. F1 score meant to have a balanced between Recall and Precision.

### Observation

- We notice that the performance will not be higher when the kernal path gets more complicates. That is, a simple AA^T matrix may outperformance every other meta path like APBPTAT. Since our benign set is balanced with malware set (same number of targets and same apk in size), our dataset is far away from real datasets. In our cases, the naive AA^T works the best for the fully balanced datasets.
- The Hindroid approach matches to hindroid paper results except for the methods involves B matrices. In this case, we suggest that the B matrix adds some noise on the Kernel matrix when training since our data set only consists the feature CSV files with less than 5MB. We suggest that as the apk files being smaller, the weights of B will be getting larger, and then the noise of Block will impact the overall performance. We assume that with larger apk files trained into the model, the weights of the noise of B will be smaller, then the performance will get better. In other words, we make the hypothesis that the B matrix will benefit the model as apk files as the training set getting larger and larger.

## Conclusion & Discussion

### Data Ingestion Pipeline

- For data downloading, we can download 2000+ apk in 5 minutes on DSMLP by taking advantage of parallelism in dask.
- For apk file decompiling, it took us nearly 10 hours to ingest those apk files to smali code. We question our techniques with the following two points:
    - The `I/O cost` in DSMLP, in downloading process, downloads files very fast and stores in the disk. The APK tool is designed to decompile apks one by one, and it only support decompile apk in the disk. When we are using DSMLP, the decompiling time would be doubled than we decompile on an SSD-driven laptop. So the I/O cost comes a big issue if we want to process a large amount of training data of smalis.
    - The poor `parallelism implemented in dask` when dealing with python subprocess. We used dask to manage the parallelism because of its higher-level task management and pandas-like API. It may work poorly when we parallel tasks in the python subprocess.

### Feature Extraction

- For feature extraction, we also used pandas to extract each file with reading smali code files, and we used dask to parallel our tasks. For feature extraction of 2000+ apk, the total task took 5 hours. The tasks are expensive when we need larger datasets. We also question our techniques with `I/O cost` and `parallelism implemented in dask` mentioned in Data Ingestion Pipeline.

### Model Metrics Performance

- Compared to the baseline model which utilizes the statistical meaning of each feature, the hindroid approach is more reliable when the dataset comes larger in general. From our experimental results of hindroid, we have some unsolved questions and hypotheses: `how the results will be as variety data trained into model`.
- In specific, `how will P and B impact the classification as variety of datasets trained in`. In the original paper of Hindroid, the ABA^T and AA^T outperform all other meta paths. In our results, AA^T also outperforms others, but ABA^T performs even worse than our Random Forest in the baseline model. We made the hypothesis that `B matrix works as a dropout layer to serve as a regulator to penalize over-fitting` since there exists a sign of over-fitting in the AA^T meta path. To confirm such an assumption, we need to ingest more datasets and see the training results.

### Model Computational Efficiency

- In `the training` process, the Basedline and Hindroid models both use a `spark` to preprocess data and constructing a matrix. The training process is surprisingly fast when we have 40 samples, the training process of both of them takes a few seconds (a few minutes in pure pandas). With 810 samples, the training process of both of them takes a few minutes (a few hours in pure pandas with memory concern). Also, more importantly, memory usage is very low. We suggest that even in I matrix (not implemented), our approach will still be solid and good.
- In`validation` and `testing`, we did our approaches in a pure scikit-learn pipeline with no joblib parameters (no parallelism and distributed computing). For validation and testing over 40 samples, the baseline model takes a few seconds and hindroid model takes about 20+ seconds. For validation and testing over 810 samples, the baseline model takes about two minutes and the hindroid model takes about five minutes.

### Concern and Future

As of right now, we have a full scope of how a project is been constructed, and we did several times roll-back in my development. i.e. we first constructed my training model process in dask, and it took forever to train, and then we switched to pyspark. Also, we still were still fixing our data ingestion pipeline when we were in the training process, etc. We are sure that roll-back cases will still happen in the future deployment of the next project, but we want to avoid them as much as possible. We have the following improvements and concerns for future implementation:

- data ingestion pipeline:
    - `I/O cost`, to reduce the I/O cost, we can get the source code of the API Tool and twist it into an In-memory decompile tool to make the data ingestion pipeline faster.
    - `Parallelism`. We may think about switching to command-line own parallelism or other distributed computing library.
- feature extraction:
    - `I/O cost`, to reduce the I/O cost, we can integrate the feature extraction process in data ingestion pipeline to do in-memory computing.
    - `Parallelism`. Using `spark` to do data frame/tabular operation.
- model metrics performance:
    - `Classifier` the paper uses SVM to classify the preprocessed matrices, we can change different estimators to try out the results. i.e. We can use some tree-based algorithm like XGBoost to see if the performance will be better.
- model computational efficiency:
    - `Training`: Since the computational efficiency for the training process is fairly good after the switch to spark, we do not have any concern about it so far.
    - `Testing and Validation`: we can also switch our training, validation pipeline into the spark by using packages under spark.mlib. We can make the whole training and testing pipeline in Spark.
    - `In general`, our implementation tried our best to optimize the process of preprocessing and training by trying different toolkits like Dask, Spark, etc. Downcasting the issue to a basic level, the computation is trivial because of a large number of unique api calls, packages, and blocks. I encountered a different types of memory outrage when I implemented the model. There are different approaches suggested to fix the issue:
        - `Trim Down API Calls`, Like pruning a decision tree, trimming the API calls to a fixed dictionary, the computational problem of API calls can be solved. It can also prevent the problem of overfitting.
        - `Change Embedding Method`, we can use a more highly optimized graph technique to process the algorithm.

## Reference

This page contains references on topics covered in this domain of inquiry and sometimes serves as a reference to the weekly reading, sometimes as a supplement to materials covered in the course.

The main paper being replicated in this domain is the [HinDroid](https://www.cse.ust.hk/~yqsong/papers/2017-KDD-HINDROID.pdf) paper on Malware detection.

### Malware Background

- [Computer Viruses and Malware](https://www.springer.com/us/book/9780387302362) by Aycock, John. Available for pdf download on campus networks or VPN.
- [Slides](http://cseweb.ucsd.edu/classes/sp18/cse127-a/CSE127sp18.18-Savage.pdf) for the Malware and Cybercrime lecture of CSE 127 at UCSD.
- A [reference sheet](http://pages.cpsc.ucalgary.ca/~joel.reardon/mobile/smali-cheat.pdf) for decompiling Android applications to Smali Code.

### Graph Techniques in Machine Learning

- A (graduate) [survey course](http://web.eecs.umich.edu/~dkoutra/courses/W18_598/) at Michigan on Graph Mining.

### Machine Learning on Source Code

- A [collection](https://github.com/src-d/awesome-machine-learning-on-source-code) of papers and references exploring understanding source code with machine learning.
