FROM python:3.7-slim

COPY ./app /usr/src/backend
WORKDIR /usr/src/backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "config.wsgi:application", "--bind", "0:8000" ]
