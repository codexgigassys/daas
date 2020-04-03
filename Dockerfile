FROM python:3.8.0-buster AS base
RUN mkdir /daas
WORKDIR /daas
# Install pip packages for production
COPY requirements_api.txt /tmp/requirements_api.txt
RUN pip install --upgrade pip && \
    pip --retries 10 install -r /tmp/requirements_api.txt


FROM base AS testing
# Move and join test resources
RUN mkdir /test_resources
COPY ./daas/daas_app/tests/resources /test_resources
RUN echo "Joining test resources..." && \
    cat /test_resources/flash_pack_parts/flash_pack.zip.? > \
        /test_resources/flash_pack.zip && \
    rm -rf /test_resources/flash_pack_parts && \
    echo "Resources joined"
# Install testing pip packages
COPY requirements_test.txt /tmp/requirements_test.txt
RUN pip install --upgrade pip && \
    pip --retries 10 install -r /tmp/requirements_test.txt


FROM base AS production
COPY ./daas /daas
RUN rm -rf /daas/daas_app/tests/
