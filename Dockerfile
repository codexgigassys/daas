FROM python:3.7.4-stretch
RUN mkdir /daas
WORKDIR /daas
ENV PYTHONUNBUFFERED=0
ENV HOME /home/root


RUN apt-get clean && \
apt-get update && \
apt-get install --no-install-recommends -y build-essential apt-transport-https && \
apt-get clean && \
apt-get update

ADD . /daas
RUN pip install --upgrade pip && \
    pip install -r /daas/pip_requirements_api.txt && \
    echo "Joining test resources..." && \
    cat /daas/daas/daas/daas_app/tests/resources/flash_pack_parts/flash_pack.zip.? > \
        /daas/daas/daas/daas_app/tests/resources/flash_pack_parts/flash_pack.zip
