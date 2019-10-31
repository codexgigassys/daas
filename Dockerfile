FROM python:3.8.0-buster AS base
RUN mkdir /daas
WORKDIR /daas
ENV PYTHONUNBUFFERED=0
COPY pip_requirements_api.txt /tmp/pip_requirements_api.txt
RUN pip install --upgrade pip && \
    pip --retries 10 install -r /tmp/pip_requirements_api.txt


FROM base AS testing
RUN mkdir /test_resources
COPY ./daas/daas_app/tests/resources /test_resources
RUN echo "Joining test resources..." && \
    cat /test_resources/flash_pack_parts/flash_pack.zip.? > \
        /test_resources/flash_pack.zip && \
    rm -rf /test_resources/flash_pack_parts && \
    echo "Resources joined"


FROM base AS production
COPY ./daas /daas
RUN rm -rf /daas/daas_app/tests/
