FROM python:3.7.4-stretch
RUN mkdir /daas
WORKDIR /daas
ENV PYTHONUNBUFFERED=0
ENV HOME /home/root
RUN pip install --upgrade pip
