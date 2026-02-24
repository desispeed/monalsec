FROM python:3.11-slim

# Install nmap for scanning inside the container
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
COPY aptsec/ ./aptsec/

RUN pip install --no-cache-dir -e .

# SQLite DB lives in /data so it can be mounted as a volume
ENV APTSEC_DB=/data/aptsec.db

VOLUME ["/data"]

ENTRYPOINT ["aptsec"]
CMD ["--help"]
