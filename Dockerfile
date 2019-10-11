FROM python:3.7.4-stretch
RUN mkdir /daas && \
    mkdir /test && \
    mkdir /test/resources
WORKDIR /daas
ENV PYTHONUNBUFFERED=0
ENV HOME /home/root

COPY . /daas
RUN pip install --upgrade pip && \
    pip --retries 10 install -r /daas/pip_requirements_api.txt && \
    echo "Joining test resources..." && \
    cat /daas/daas/daas_app/tests/resources/flash_pack_parts/flash_pack.zip.? > \
        /test/resources/flash_pack.zip
