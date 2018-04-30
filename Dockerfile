ROM python:2.7-stretch
RUN mkdir /myapp
WORKDIR /myapp
ADD . /myapp
ENV PYTHONUNBUFFERED=0
ENV HOME /home/root
ENV WINEARCH win32


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
winehq-devel:i386=3.5.0~stretch \
wine-devel:i386=3.5.0~stretch \
wine-devel-i386:i386=3.5.0~stretch \
fonts-wine \
cabextract \
unzip \
host && \
apt-get clean && \
apt-get update && \
wget -nc -nv https://github.com/Winetricks/winetricks/archive/20171222.zip -O /tmp/winetricks.zip && \
unzip /tmp/winetricks.zip -d /tmp/winetricks/ && \
make -C /tmp/winetricks/winetricks-20171222 install && \
rm -rf /tmp/winetricks.zip && \
rm -rf /tmp/winetricks
RUN winetricks -q dotnet45 corefonts