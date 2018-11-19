FROM nvidia/cuda:9.2-cudnn7-runtime-ubuntu18.04

WORKDIR /app
COPY requirements.txt .

RUN apt update && apt install -y python3 python3-pip curl

RUN pip3 install --no-cache -r requirements.txt && \
    curl -o /tmp/torch_nightly-1.0.0.dev20181116-cp36-cp36m-linux_x86_64.whl https://download.pytorch.org/whl/nightly/cu92/torch_nightly-1.0.0.dev20181116-cp36-cp36m-linux_x86_64.whl && \
    pip3 install torch_nightly -f /tmp/torch_nightly-1.0.0.dev20181116-cp36-cp36m-linux_x86_64.whl && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/torch_nightly-1.0.0.dev20181116-cp36-cp36m-linux_x86_64.whl

COPY *.py config.json /app/
COPY --chown=65534 models models
RUN mkdir -m 777 /nonexistent /app/feedback
USER nobody
ENTRYPOINT [ "gunicorn", "app:app", "--access-logfile", "-", "--error-logfile", "-" ]
CMD [ "-k", "gthread",  "-t", "60", "--workers", "1", "--threads", "2", "-b", "0.0.0.0" ]