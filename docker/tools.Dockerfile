FROM python:3.13-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends procps iproute2 curl \
    && rm -rf /var/lib/apt/lists/*
CMD ["sh"]
