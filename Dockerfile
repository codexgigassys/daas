FROM python:3.7.4-stretch
RUN mkdir /daas
WORKDIR /daas
ENV PYTHONUNBUFFERED=0
ENV HOME /home/root
COPY pip_requirements_api.txt /tmp/pip_requirements_api.txt
RUN pip install --upgrade pip && \
    pip --retries 10 install -r /tmp/pip_requirements_api.txt && \
    rm -rf /tmp/pip_requirements_api.txt
