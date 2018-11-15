FROM python:3-slim

WORKDIR /app

RUN pip install --no-cache locustio

COPY locustfile.py keeshond.jpg ./
USER nobody
ENTRYPOINT [ "locust" ]