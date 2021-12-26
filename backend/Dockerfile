FROM python:3.10.1-slim-buster

RUN apt-get update && \
    apt-get install -y python3-dev wget pwgen git vim \
    && \
    rm -rf /var/lib/apt

ENV SETUPTOOLS_USE_DISTUTILS=stdlib

WORKDIR /opt/service

RUN wget -qO- https://github.com/koalaman/shellcheck/releases/download/v0.8.0/shellcheck-v0.8.0.linux.x86_64.tar.xz | tar -xJf - && \
    cd shellcheck-v0.8.0/ && \
    cp shellcheck /usr/bin

COPY requirements.txt .
RUN pip install -U pip && \
    pip install -r requirements.txt

ENTRYPOINT ["./entrypoint.sh"]
