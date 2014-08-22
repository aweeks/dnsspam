FROM stackbrew/ubuntu:trusty

ADD . /tmp/dnsspam

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y --no-install-recommends python2.7 python-pip bash && \
    apt-get -y autoremove && \
    apt-get clean

RUN pip install -r /tmp/dnsspam/requirements.txt

CMD [ "/tmp/dnsspam/dnsspam.py", "--resolv", "/tmp/dnsspam/resolv.conf", "--queries", "/tmp/dnsspam/conf.json" ]
