FROM python:2.7-stretch
RUN mkdir /myapp
WORKDIR /myapp
ADD . /myapp
ENV PYTHONUNBUFFERED=0
ENV HOME /home/root
ENV WINEARCH win32


RUN mv -v /myapp/utils/just_decompile /just_decompile && \
apt-get clean && \
apt-get update && \
apt-get install --no-install-recommends -y build-essential apt-transport-https && \
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
xauth \
winehq-devel:i386=3.5.0~stretch \
wine-devel:i386=3.5.0~stretch \
wine-devel-i386:i386=3.5.0~stretch \
fonts-wine \
cabextract \
zenity \
xvfb \
host && \
apt-get clean && \
apt-get update && \
echo "Installing winetricks" && \
wget -nc -nv https://github.com/Winetricks/winetricks/archive/20171222.zip -O /tmp/winetricks.zip && \
unzip /tmp/winetricks.zip -d /tmp/winetricks/ && \
make -C /tmp/winetricks/winetricks-20171222 install && \
rm -rf /tmp/winetricks.zip && \
rm -rf /tmp/winetricks && \
echo "Winetricks installed"
RUN timeout 4500 winetricks -q dotnet45 corefonts; if [ $? -eq 124 ]; then echo "Status is 124. Retrying dotnet45 installation..." && date && timeout 1000 winetricks -q dotnet45 corefonts; if [ $? -eq 124 ]; then "Status is 124 again(!). Retrying dotnet45 installation without timeout..." && date && winetricks -q dotnet45 corefonts; else echo "Status is not 124"; fi; else echo "Status is not 124."; fi; \
echo "Winetricks installed" && \
echo "Overriding system dll" && \
wget -nc -nv https://download.dll-files.com/e5f7c30edf0892667933be879f067d67/msvcr100_clr0400.zip?LzJMNHhVWit1ZkZEUkhFTEpVN0hkUT09 -O /tmp/override_dll.zip && \
unzip /tmp/override_dll.zip -d /tmp/override_dll/ && \
cp /tmp/override_dll/msvcr100_clr0400.dll /just_decompile/msvcr100_clr0400 && \
rm -rf /tmp/override_dll.zip && \
rm -rf /tmp/override_dll && \
echo "System dll overriden!"