FROM python:3.7.0-stretch
RUN mkdir /daas
WORKDIR /daas
ADD . /daas
ENV PYTHONUNBUFFERED=0
ENV HOME /home/root

RUN apt-get clean && \
apt-get update && \
apt-get install --no-install-recommends -y build-essential apt-transport-https && \
apt-get clean && \
apt-get update

RUN cd /tmp/ && \
wget  https://deb.nodesource.com/setup_8.x && \
echo 'deb https://deb.nodesource.com/node_8.x  stretch  main' > /etc/apt/sources.list.d/nodesource.list && \
wget -qO - https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
apt update && \
apt install nodejs && \
npm install -g bower

RUN pip install -r /daas/pip_requirements_api.txt

# Do not use bower install (without "_") because it's bugged
RUN python /daas/daas/manage.py bower_install --allow-root
RUN python /daas/daas/manage.py collectstatic --no-input