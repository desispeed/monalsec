# aptsec Containerization Design

**Date:** 2026-02-23
**Topic:** Containerize the aptsec CLI pentest tool using Docker

## Overview

Containerize `aptsec` so it runs as a portable Docker image invoked with `docker run --rm` per command, with data persisted in a named Docker volume and a shell alias for native CLI feel.

## Architecture

### Dockerfile

- Base: `python:3.11-slim`
- Working dir: `/app`
- Install: `pip install .` from copied source
- Default env: `APTSEC_DB=/data/aptsec.db`
- Entrypoint: `aptsec`

### Data Persistence

- Named Docker volume: `aptsec-data`
- Mounted at `/data` inside the container
- Contents:
  - `/data/aptsec.db` — SQLite database (all engagements, findings, targets)
  - `/data/reports/` — generated PDF reports

### File I/O

- Nmap XML import: host's current working directory mounted at `/input`
- PDF report output: host's current working directory mounted at `/output`
- Both mounts handled via shell aliases

### Shell Aliases

Two aliases added to `~/.zshrc`:

```bash
alias aptsec='docker run --rm -v aptsec-data:/data -v "$PWD":/input aptsec'
alias aptsec-report='docker run --rm -v aptsec-data:/data -v "$PWD":/output aptsec'
```

- `aptsec` — for all commands; nmap files referenced as `/input/<filename>`
- `aptsec-report` — for report generation; output written to `/output/<filename>` (lands in current dir)

## Usage After Containerization

```bash
# Build
docker build -t aptsec /Users/monalvalia/aptsec

# Create volume (one-time)
docker volume create aptsec-data

# Normal usage (via alias)
aptsec engagement create --name "Acme Corp" --target "192.168.1.0/24" --tester "Alice"
aptsec engagement list
aptsec finding add --engagement 1 --title "SQLi" --severity critical --category Web --description "..." --remediation "..."
aptsec import nmap --file /input/scan.xml --engagement 1
aptsec-report report generate --engagement 1 --output /output/report.pdf
```

## Files Changed

| File | Action |
|------|--------|
| `Dockerfile` | Create |
| `~/.zshrc` | Append aliases |

## Trade-offs

- **Named volume** over host-mounted dir: data stays managed by Docker, not directly browsable as a folder on the Mac — acceptable since primary access is via the CLI
- **Single-stage build** over multi-stage: simpler Dockerfile; image size (~200 MB) is acceptable for a developer tool
- **Shell aliases** for file I/O: cleaner than requiring full `-v` flags every invocation
