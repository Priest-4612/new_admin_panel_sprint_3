FROM python:3.7-slim

COPY ./elt /usr/src/elt
WORKDIR /usr/src/backend

RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir
