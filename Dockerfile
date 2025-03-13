# Dockerfile for netprobe
# https://github.com/plaintextpackets/netprobe_lite/
FROM ghcr.io/astral-sh/uv:python3.13-alpine

ENV PYTHONUNBUFFERED=1

# install ip utils to get a ping with jitter data in the output
RUN apk add --no-cache iputils
# install speedtest-rs
RUN apk add --no-cache tar curl && \
    cd /tmp && \
    curl -sSL https://github.com/showwin/speedtest-go/releases/download/v1.7.10/speedtest-go_1.7.10_Linux_x86_64.tar.gz | tar xz && \
    mv /tmp/speedtest-go /usr/local/bin/speedtest-go && \
    rm -rf /tmp/*

# install librespeed-cli
COPY --from=ghcr.io/danieletorelli/librespeed-cli /usr/local/bin/librespeed-cli /bin/

WORKDIR /netprobe_lite

COPY pyproject.toml uv.lock src .

# install project
RUN uv sync --frozen

ENTRYPOINT [ "uv", "run", "main.py" ]
