# aptsec

A command-line pentest findings aggregator and PDF report generator for individual security researchers and penetration testers.

## Features

- Manage multiple engagements (client name, target scope, tester)
- Import open ports from Nmap XML output
- Add manual findings with severity, category, description, evidence, and remediation
- Generate professional PDF reports (cover page, executive summary, findings, appendix)

## Requirements

- Python 3.11+
- Dependencies: `click`, `reportlab`, `lxml`, `rich`

## Installation

```bash
git clone https://github.com/desispeed/monalsec.git
cd monalsec
pip install -e .
```

## Usage

### Engagements

```bash
# Create a new engagement
aptsec engagement create --name "Acme Corp" --target "192.168.1.0/24" --tester "Alice"

# List all engagements
aptsec engagement list

# Show engagement details
aptsec engagement show --id 1
```

### Import Tool Output

```bash
# Import Nmap XML results
aptsec import nmap --file scan.xml --engagement 1
```

### Findings

```bash
# Add a manual finding
aptsec finding add \
  --engagement 1 \
  --title "Weak password policy" \
  --severity high \
  --category Web \
  --description "No account lockout after failed attempts" \
  --remediation "Implement account lockout after 5 failed attempts"

# List findings for an engagement
aptsec finding list --engagement 1

# Delete a finding
aptsec finding delete --id 3
```

Severity levels: `critical`, `high`, `medium`, `low`, `info`

Categories: `Network`, `Web`, `API`, `Mobile`

### Reports

```bash
# Generate a PDF report
aptsec report generate --engagement 1 --output report.pdf
```

The PDF includes:
- Cover page with engagement metadata
- Executive summary with severity breakdown table
- Detailed findings (description, evidence, remediation, CVSS score if set)
- Appendix of all discovered targets from automated imports

## Data Storage

By default, data is stored at `~/aptsec.db`. Override with the `APTSEC_DB` environment variable:

```bash
APTSEC_DB=/path/to/custom.db aptsec engagement list
```

## Development

```bash
pip install -e .
pytest
```

## License

MIT
