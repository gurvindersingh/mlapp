FROM python:3-slim

WORKDIR /app
COPY requirements.txt .

RUN apt update && apt install -y gcc && \
    pip install --no-cache -r requirements.txt && \
    pip install --no-cache torch_nightly -f https://download.pytorch.org/whl/nightly/cpu/torch_nightly.html && \
    apt autoremove -y gcc && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY *.py config.json /app/
COPY --chown=65534 models models
RUN mkdir -m 777 /nonexistent /app/feedback
USER nobody
ENTRYPOINT [ "gunicorn", "app:app", "--access-logfile", "-", "--error-logfile", "-" ]
CMD [ "-k", "gthread",  "-t", "60", "--workers", "1", "--threads", "2", "-b", "0.0.0.0" ]