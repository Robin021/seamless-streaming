# build frontend with node
FROM node:20-alpine AS frontend
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY streaming-react-app .
RUN \
    if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
    elif [ -f package-lock.json ]; then npm ci; \
    elif [ -f pnpm-lock.yaml ]; then yarn global add pnpm && pnpm i --frozen-lockfile; \
    else echo "Lockfile not found." && exit 1; \
    fi

RUN npm run build

# build backend on CUDA 
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04 AS backend
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_MAJOR=20

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    git \
    git-lfs \
    wget \
    curl \
    # python build dependencies \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    sox libsox-fmt-all \
    # gradio dependencies \
    ffmpeg \
    # fairseq2 dependencies \
    libsndfile-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

RUN curl https://pyenv.run | bash
ENV PATH=$HOME/.pyenv/shims:$HOME/.pyenv/bin:$PATH
ARG PYTHON_VERSION=3.10.12
RUN pyenv install $PYTHON_VERSION && \
    pyenv global $PYTHON_VERSION && \
    pyenv rehash && \
    pip install --no-cache-dir -U pip setuptools wheel

COPY --chown=user:user ./seamless_server ./seamless_server
# change dir since pip needs to seed whl folder
RUN cd seamless_server && pip install --no-cache-dir --upgrade -r requirements.txt
COPY --from=frontend /app/dist ./streaming-react-app/dist

WORKDIR $HOME/app/seamless_server
# temporary hack to link SeamlessStreaming models
ARG HF_TOKEN
ENV HF_TOKEN=$HF_TOKEN
RUN huggingface-cli download meta-private/SeamlessStreaming seamless_streaming_unity.pt spm_char_lang38_tc.model seamless_streaming_monotonic_decoder.pt --local-dir ./models/ && \
    huggingface-cli download meta-private/SeamlessExpressive pretssel_melhifigan_wm-final.pt  --local-dir ./models/ 
USER root
RUN mkdir -p /large_experiments/seamless/ust/krs/fairseq2_checkpoints/ && \
    mkdir -p /large_experiments/seamless/workstream/expressivity/oss/checkpoints/ && \
    mkdir -p /checkpoint/krs/unity2/ && \
    chown -R user:user /large_experiments/ && \
    chown -R user:user /checkpoint/ && \
    ln -s $(readlink -f models/seamless_streaming_unity.pt) /large_experiments/seamless/ust/krs/fairseq2_checkpoints/seamless_streaming_unity.pt && \
    ln -s $(readlink -f models/seamless_streaming_monotonic_decoder.pt) /large_experiments/seamless/ust/krs/fairseq2_checkpoints/seamless_streaming_monotonic_decoder.pt && \
    ln -s $(readlink -f models/pretssel_melhifigan_wm-final.pt) /large_experiments/seamless/workstream/expressivity/oss/checkpoints/pretssel_melhifigan_wm-final.pt && \
    ln -s $(readlink -f models/spm_char_lang38_tc.model) /checkpoint/krs/unity2/

RUN ln -s /usr/lib/x86_64-linux-gnu/libsox.so.3 /usr/lib/x86_64-linux-gnu/libsox.so
USER user
CMD [ "uvicorn", "app_pubsub:app", "--host", "0.0.0.0", "--port", "7860" ]


