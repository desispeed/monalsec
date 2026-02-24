# aptsec Containerization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Package `aptsec` as a Docker image with a named volume for persistence and shell aliases for native CLI feel.

**Architecture:** Single-stage `python:3.11-slim` image installs `aptsec` from local source; a named volume `aptsec-data` persists the SQLite database at `/data/aptsec.db`; two `.zshrc` aliases make the container transparent to the user.

**Tech Stack:** Docker, Python 3.11-slim base image, bash/zsh aliases

---

### Task 1: Create `.dockerignore`

**Files:**
- Create: `aptsec/.dockerignore`

**Step 1: Create the file**

```
.venv/
__pycache__/
*.pyc
*.egg-info/
.pytest_cache/
.git/
aptsec.db
dist/
docs/
tests/
```

Save this as `/Users/monalvalia/aptsec/.dockerignore`.

**Step 2: Verify the file exists**

Run: `cat /Users/monalvalia/aptsec/.dockerignore`
Expected: File contents printed with the entries above.

**Step 3: Commit**

```bash
cd /Users/monalvalia/aptsec
git add .dockerignore
git commit -m "chore: add .dockerignore for Docker build"
```

---

### Task 2: Create `Dockerfile`

**Files:**
- Create: `aptsec/Dockerfile`

**Step 1: Create the Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir .

ENV APTSEC_DB=/data/aptsec.db

ENTRYPOINT ["aptsec"]
```

Save as `/Users/monalvalia/aptsec/Dockerfile`.

**Step 2: Verify the file**

Run: `cat /Users/monalvalia/aptsec/Dockerfile`
Expected: File contents match exactly.

**Step 3: Commit**

```bash
cd /Users/monalvalia/aptsec
git add Dockerfile
git commit -m "feat: add Dockerfile for aptsec containerization"
```

---

### Task 3: Build the Docker image

**Files:** none

**Step 1: Build the image**

Run: `docker build -t aptsec /Users/monalvalia/aptsec`

Expected: Build completes with output ending in:
```
Successfully tagged aptsec:latest
```
(or `=> => naming to docker.io/library/aptsec` in BuildKit output)

**Step 2: Verify the image exists**

Run: `docker images aptsec`
Expected: A row with `aptsec` as REPOSITORY and `latest` as TAG.

**Step 3: Smoke-test the image**

Run: `docker run --rm aptsec --help`
Expected: aptsec CLI help text printed (Usage, Options, Commands).

---

### Task 4: Create the named Docker volume

**Files:** none

**Step 1: Create the volume**

Run: `docker volume create aptsec-data`
Expected: `aptsec-data`

**Step 2: Verify the volume exists**

Run: `docker volume inspect aptsec-data`
Expected: JSON output with `"Name": "aptsec-data"` and a `Mountpoint` path.

---

### Task 5: End-to-end test with volume (before adding aliases)

**Files:** none

**Step 1: Create a test engagement**

Run:
```bash
docker run --rm -v aptsec-data:/data aptsec engagement create \
  --name "Test Corp" --target "10.0.0.0/8" --tester "Alice"
```
Expected: Output shows engagement created (ID 1).

**Step 2: List engagements — verify persistence works**

Run: `docker run --rm -v aptsec-data:/data aptsec engagement list`
Expected: Table showing the "Test Corp" engagement.

**Step 3: Add a finding**

Run:
```bash
docker run --rm -v aptsec-data:/data aptsec finding add \
  --engagement 1 \
  --title "Open admin panel" \
  --severity high \
  --category Web \
  --description "Admin panel accessible without auth" \
  --remediation "Restrict access behind VPN"
```
Expected: Finding created confirmation.

**Step 4: Generate a PDF report to current directory**

Run:
```bash
docker run --rm -v aptsec-data:/data -v "$PWD":/output aptsec \
  report generate --engagement 1 --output /output/test_report.pdf
```
Expected: `test_report.pdf` appears in the current directory.

**Step 5: Verify the PDF**

Run: `ls -lh test_report.pdf`
Expected: File exists with non-zero size (typically 10–100 KB).

**Step 6: Clean up test data**

Run:
```bash
docker run --rm -v aptsec-data:/data aptsec finding delete --id 1
docker run --rm -v aptsec-data:/data aptsec engagement list
```
Then remove the test volume data:
```bash
docker volume rm aptsec-data && docker volume create aptsec-data
```
This resets the DB for real use.

---

### Task 6: Add shell aliases to `~/.zshrc`

**Files:**
- Modify: `~/.zshrc`

**Step 1: Append aliases to .zshrc**

Add the following block to the end of `/Users/monalvalia/.zshrc`:

```bash
# aptsec - containerized pentest findings tool
alias aptsec='docker run --rm -v aptsec-data:/data -v "$PWD":/input aptsec'
alias aptsec-report='docker run --rm -v aptsec-data:/data -v "$PWD":/output aptsec'
```

**Step 2: Reload shell config**

Run: `source ~/.zshrc`
Expected: No errors.

**Step 3: Verify aliases are registered**

Run: `alias | grep aptsec`
Expected:
```
aptsec='docker run --rm -v aptsec-data:/data -v "$PWD":/input aptsec'
aptsec-report='docker run --rm -v aptsec-data:/data -v "$PWD":/output aptsec'
```

---

### Task 7: Final end-to-end test via aliases

**Files:** none

**Step 1: Create an engagement via alias**

Run: `aptsec engagement create --name "Acme Corp" --target "192.168.1.0/24" --tester "Alice"`
Expected: Engagement created (ID 1).

**Step 2: List engagements**

Run: `aptsec engagement list`
Expected: Table with "Acme Corp".

**Step 3: Add a finding**

Run:
```bash
aptsec finding add \
  --engagement 1 \
  --title "Weak password policy" \
  --severity high \
  --category Web \
  --description "No account lockout after 5 failed attempts" \
  --remediation "Implement account lockout policy"
```
Expected: Finding added confirmation.

**Step 4: Generate PDF report to current directory**

Run: `aptsec-report report generate --engagement 1 --output /output/acme_report.pdf`
Expected: `acme_report.pdf` appears in current directory.

**Step 5: Verify PDF**

Run: `ls -lh acme_report.pdf`
Expected: Non-zero size PDF file.

**Step 6: Test nmap import path (dry run)**

Run: `aptsec import nmap --file /input/nonexistent.xml --engagement 1`
Expected: Error message about file not found (proves the `/input` mount works — replace with a real nmap XML file when needed).

---

## Usage Reference (post-implementation)

```bash
# Build image (re-run after code changes)
docker build -t aptsec /Users/monalvalia/aptsec

# All commands use the alias
aptsec engagement create --name "Client" --target "10.0.0.0/8" --tester "You"
aptsec engagement list
aptsec finding add --engagement 1 --title "..." --severity critical --category Web --description "..." --remediation "..."
aptsec import nmap --file /input/scan.xml --engagement 1   # scan.xml must be in $PWD
aptsec-report report generate --engagement 1 --output /output/report.pdf
```
