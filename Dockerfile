FROM tensorflow/tensorflow:latest-py3

# ソースを置くディレクトリを変数として格納                                                  
ARG project_dir=/work

# 必要なファイルをローカルからコンテナにコピー
RUN mkdir -p $project_dir

# requirements.txtに記載されたパッケージをインストール                         
WORKDIR $project_dir
ADD ./requirements.txt $project_dir

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# install packages used inside container (optional)
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    && apt-get autoremove \
    && apt-get clean
