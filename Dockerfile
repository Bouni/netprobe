# Dockerfile for netprobe_lite
# https://github.com/plaintextpackets/netprobe_lite/
FROM python:3.13-alpine

ENV PYTHONUNBUFFERED=1

# install ip utils to get a ping with jitter data in the output
RUN apk add iputils speedtest-cli

# Install uv (https://github.com/astral-sh/uv)
COPY --from=ghcr.io/astral-sh/uv:python3.13-alpine /usr/local/bin/uv /usr/local/bin/uvx /bin/

WORKDIR /netprobe_lite

COPY pyproject.toml .
COPY uv.lock .

# install project
RUN uv sync --frozen

# copy python files into the container
COPY src .

ENTRYPOINT [ "uv", "run", "main.py" ]
