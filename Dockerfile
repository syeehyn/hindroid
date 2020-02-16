FROM amfraenkel/android-malware-project
USER root
# python3 setup
RUN apt-get update && apt-get install -y graphviz

RUN conda install -c anaconda --yes  \
            snakeviz  \
            distributed \
            ipywidgets \
    && conda install -c conda-forge --yes \
            nodejs \
            jupyterlab \
            dask-ml \
            toolz \
            dask-labextension \
            s3fs  \
            fastparquet \
            python-graphviz \
    && conda install --yes \
            dask \
            h5py \
            bokeh
    