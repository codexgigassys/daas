FROM python:3.7.0-stretch
RUN mkdir /daas
WORKDIR /daas
ADD . /daas
ENV PYTHONUNBUFFERED=0
ENV HOME /home/root
RUN pip install --upgrade pip

RUN apt-get clean && \
apt-get update && \
apt-get install --no-install-recommends -y build-essential apt-transport-https && \
apt-get clean && \
apt-get update

RUN pip install -r /daas/pip_requirements_api.txt
