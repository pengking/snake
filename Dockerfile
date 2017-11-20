FROM gw000/keras:2.0.6-py2-tf-cpu

COPY ./requirements.txt /
ADD ./jessie-sources.list /etc/apt/sources.list
RUN apt-get update \
    && apt-get -y --no-install-recommends install build-essential \
    && pip install -r /requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    && apt-get purge -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

CMD jupyter notebook --no-browser --ip=0.0.0.0 --port=8888 --allow-root
