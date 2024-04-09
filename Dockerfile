FROM python:3.11-slim-bullseye

RUN rm -rf /usr/local/cuda/lib64/stubs

WORKDIR /app

ENV HOME=/app
ENV USE_TORCH=1
ENV DEBIAN_FRONTEND=noninteractive

COPY --link requirements.txt ./

COPY --link . .

RUN set -x \
    && apt-get update \
    && apt-get -y install --no-install-recommends \
        curl \
        gcc \
        musl-dev \
        python3 \
        python3-dev \
        python3-pip \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --user -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cu118

CMD [ "python3" , "/app/app.py" ]