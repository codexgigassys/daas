ROM python:2.7-stretch
RUN mkdir /myapp
WORKDIR /myapp
ADD . /myapp
ENV PYTHONUNBUFFERED=0
ENV HOME /home/root


RUN mv -v /myapp/utils/just_decompile /just_decompile && \
apt-get clean && \
apt-get update && \
apt-get install -y build-essential apt-transport-https && \
dpkg --add-architecture i386 && \
apt-get clean && \
apt-get update && \
wget -nc https://dl.winehq.org/wine-builds/Release.key && \
apt-key add Release.key && \
echo "deb https://dl.winehq.org/wine-builds/debian/ stretch main" >> /etc/apt/sources.list.d/wine.list && \
apt-get clean && \
apt-get update && \
apt install --assume-yes gnutls-bin \
unzip \
winehq-devel:i386 \
wine-devel:i386 \
wine-devel-i386:i386 \
fonts-wine \
cabextract \
unzip \
host && \
apt-get clean && \
apt-get update