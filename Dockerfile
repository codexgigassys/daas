ROM python:2.7-stretch
RUN mkdir /myapp
WORKDIR /myapp
ADD . /myapp
ENV PYTHONUNBUFFERED=0
ENV HOME /home/root