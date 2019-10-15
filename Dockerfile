FROM python:3.8.0rc1-buster
RUN mkdir /daas
WORKDIR /daas
ENV PYTHONUNBUFFERED=0
ENV HOME /home/root
COPY pip_requirements_api.txt /tmp/pip_requirements_api.txt
RUN pip install --upgrade pip && \
    pip --retries 10 install -r /tmp/pip_requirements_api.txt && \
    rm -rf /tmp/pip_requirements_api.txt
