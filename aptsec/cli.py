import os
import sys
import click
from rich.console import Console
from rich.table import Table
from aptsec.db import get_connection, init_db
from aptsec.models import (
    create_engagement, get_engagement, list_engagements,
    create_finding, list_findings, get_finding, delete_finding,
    create_target, list_targets,
)
from aptsec.parsers.nmap import parse_nmap_xml

console = Console()

SEVERITY_COLORS = {
    "critical": "red", "high": "orange3",
    "medium": "yellow", "low": "blue", "info": "dim",
}

_db_initialized_path: str | None = None


def get_db():
    global _db_initialized_path
    path = os.environ.get("APTSEC_DB", os.path.expanduser("~/aptsec.db"))
    conn = get_connection(path)
    if _db_initialized_path != path:
        init_db(conn)
        _db_initialized_path = path
    return conn


@click.group()
def cli():
    """aptsec — pentest findings aggregator and report generator."""


# ── Engagement commands ───────────────────────────────────────────────────────

@cli.group()
def engagement():
    """Manage engagements."""


@engagement.command("create")
@click.option("--name", required=True, help="Engagement / client name")
@click.option("--target", required=True, help="Scope (domain, IP range, app)")
@click.option("--tester", default="", help="Tester name for report")
def engagement_create(name, target, tester):
    db = get_db()
    eid = create_engagement(db, name=name, target=target, tester=tester)
    console.print(f"[green]Created engagement #{eid}:[/green] {name}")


@engagement.command("list")
def engagement_list():
    db = get_db()
    rows = list_engagements(db)
    if not rows:
        console.print("No engagements found. Use [bold]aptsec engagement create[/bold].")
        return
    table = Table(title="Engagements")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Target")
    table.add_column("Tester")
    table.add_column("Created")
    for r in rows:
        table.add_row(str(r["id"]), r["name"], r["target"], r["tester"], r["created_at"])
    console.print(table)


@engagement.command("show")
@click.option("--id", "eid", required=True, type=int)
def engagement_show(eid):
    db = get_db()
    eng = get_engagement(db, eid)
    if not eng:
        console.print(f"[red]Engagement #{eid} not found.[/red]")
        sys.exit(1)
    console.print(f"[bold]#{eng['id']} {eng['name']}[/bold]")
    console.print(f"Target:  {eng['target']}")
    console.print(f"Tester:  {eng['tester']}")
    console.print(f"Created: {eng['created_at']}")
    findings = list_findings(db, eid)
    console.print(f"Findings: {len(findings)}")


# ── Finding commands ──────────────────────────────────────────────────────────

@cli.group()
def finding():
    """Manage findings."""


@finding.command("add")
@click.option("--engagement", "eid", required=True, type=int)
@click.option("--title", required=True)
@click.option("--severity", required=True,
              type=click.Choice(["critical", "high", "medium", "low", "info"]))
@click.option("--category", default="Network",
              type=click.Choice(["Network", "Web", "API", "Mobile"]))
@click.option("--description", default="")
@click.option("--evidence", default="")
@click.option("--remediation", default="")
@click.option("--cvss", default=None, type=float)
def finding_add(eid, title, severity, category, description, evidence, remediation, cvss):
    db = get_db()
    fid = create_finding(
        db, engagement_id=eid, title=title, severity=severity,
        category=category, description=description, evidence=evidence,
        remediation=remediation, tool_source="manual", cvss_score=cvss,
    )
    console.print(f"[green]Added finding #{fid}:[/green] {title} ({severity})")


@finding.command("list")
@click.option("--engagement", "eid", required=True, type=int)
def finding_list(eid):
    db = get_db()
    rows = list_findings(db, eid)
    if not rows:
        console.print("No findings.")
        return
    table = Table(title=f"Findings — Engagement #{eid}")
    table.add_column("ID", style="dim")
    table.add_column("Severity")
    table.add_column("Category")
    table.add_column("Title")
    table.add_column("Source")
    for r in rows:
        color = SEVERITY_COLORS.get(r["severity"], "white")
        table.add_row(
            str(r["id"]),
            f"[{color}]{r['severity']}[/{color}]",
            r["category"], r["title"], r["tool_source"],
        )
    console.print(table)


@finding.command("delete")
@click.option("--id", "fid", required=True, type=int)
def finding_delete(fid):
    db = get_db()
    f = get_finding(db, fid)
    if not f:
        console.print(f"[red]Finding #{fid} not found.[/red]")
        sys.exit(1)
    delete_finding(db, fid)
    console.print(f"[green]Deleted finding #{fid}.[/green]")


# ── Import commands ───────────────────────────────────────────────────────────

@cli.group("import")
def import_cmd():
    """Import tool output."""


@import_cmd.command("nmap")
@click.option("--file", "filepath", required=True, type=click.Path(exists=True))
@click.option("--engagement", "eid", required=True, type=int)
def import_nmap(filepath, eid):
    db = get_db()
    eng = get_engagement(db, eid)
    if not eng:
        console.print(f"[red]Engagement #{eid} not found.[/red]")
        sys.exit(1)
    try:
        entries = parse_nmap_xml(filepath)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    imported = 0
    for entry in entries:
        create_target(
            db, engagement_id=eid,
            host=entry["host"], port=entry["port"],
            protocol=entry["protocol"], service=entry["service"],
            state=entry["state"],
        )
        # Create a finding for each open port
        title = f"Open port {entry['port']}/{entry['protocol']} ({entry['service']}) on {entry['host']}"
        create_finding(
            db, engagement_id=eid, title=title, severity="info",
            category="Network", description=f"Service: {entry['service']}",
            evidence="", remediation="Review if this service should be exposed.",
            tool_source="nmap",
        )
        imported += 1

    console.print(f"[green]Imported {imported} open port(s) from {filepath}[/green]")


# ── Report commands ───────────────────────────────────────────────────────────

@cli.group()
def report():
    """Generate reports."""


@report.command("generate")
@click.option("--engagement", "eid", required=True, type=int)
@click.option("--output", required=True, type=click.Path())
def report_generate(eid, output):
    from aptsec.report.generator import generate_pdf
    db = get_db()
    try:
        generate_pdf(db, engagement_id=eid, output_path=output)
        console.print(f"[green]Report saved to {output}[/green]")
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)
