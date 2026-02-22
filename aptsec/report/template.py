from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)

SEVERITY_COLORS = {
    "critical": colors.HexColor("#c0392b"),
    "high":     colors.HexColor("#e67e22"),
    "medium":   colors.HexColor("#f1c40f"),
    "low":      colors.HexColor("#2980b9"),
    "info":     colors.HexColor("#95a5a6"),
}

# Hex strings for XML font color tags (hexval() returns '0xRRGGBB', so we reformat)
SEVERITY_HEX = {
    sev: "#%06x" % int(c.hexval(), 16)
    for sev, c in SEVERITY_COLORS.items()
}

STYLES = getSampleStyleSheet()
HEADING1 = ParagraphStyle("Heading1Bold", parent=STYLES["Heading1"], fontSize=18, spaceAfter=12)
HEADING2 = ParagraphStyle("Heading2Bold", parent=STYLES["Heading2"], fontSize=14, spaceAfter=8)
BODY     = STYLES["Normal"]
SMALL    = ParagraphStyle("Small", parent=STYLES["Normal"], fontSize=8, textColor=colors.grey)


def build_cover(eng) -> list:
    elements = []
    elements.append(Spacer(1, 4 * cm))
    elements.append(Paragraph("PENETRATION TEST REPORT", HEADING1))
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(Paragraph(f"<b>Engagement:</b> {eng['name']}", BODY))
    elements.append(Paragraph(f"<b>Target:</b> {eng['target']}", BODY))
    elements.append(Paragraph(f"<b>Tester:</b> {eng['tester']}", BODY))
    elements.append(Paragraph(f"<b>Date:</b> {eng['created_at'][:10]}", BODY))
    elements.append(Spacer(1, 1 * cm))
    elements.append(Paragraph(
        "CONFIDENTIAL — This report contains sensitive security information. "
        "Distribution is restricted to authorized personnel only.", SMALL
    ))
    elements.append(PageBreak())
    return elements


def build_executive_summary(findings: list) -> list:
    from collections import Counter
    elements = [Paragraph("Executive Summary", HEADING1)]
    counts = Counter(f["severity"] for f in findings)
    data = [["Severity", "Count"]] + [
        [sev.capitalize(), str(counts.get(sev, 0))]
        for sev in ("critical", "high", "medium", "low", "info")
    ]
    table = Table(data, colWidths=[6 * cm, 3 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f8f8")]),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5 * cm))
    total = len(findings)
    critical = counts.get("critical", 0)
    high = counts.get("high", 0)
    elements.append(Paragraph(
        f"This engagement identified {total} finding(s), including "
        f"{critical} critical and {high} high severity issue(s) requiring immediate attention.",
        BODY,
    ))
    elements.append(PageBreak())
    return elements


def build_findings_section(findings: list) -> list:
    elements = [Paragraph("Findings", HEADING1)]
    for f in findings:
        hex_color = SEVERITY_HEX.get(f["severity"], "#808080")
        elements.append(Spacer(1, 0.3 * cm))
        elements.append(Paragraph(
            f'<font color="{hex_color}">[{f["severity"].upper()}]</font> {f["title"]}',
            HEADING2,
        ))
        elements.append(Paragraph(f"<b>Category:</b> {f['category']}", BODY))
        if f["cvss_score"]:
            elements.append(Paragraph(f"<b>CVSS Score:</b> {f['cvss_score']}", BODY))
        elements.append(Paragraph("<b>Description:</b>", BODY))
        elements.append(Paragraph(f["description"] or "—", BODY))
        elements.append(Paragraph("<b>Evidence:</b>", BODY))
        elements.append(Paragraph(f["evidence"] or "—", BODY))
        elements.append(Paragraph("<b>Remediation:</b>", BODY))
        elements.append(Paragraph(f["remediation"] or "—", BODY))
        elements.append(Spacer(1, 0.3 * cm))
    elements.append(PageBreak())
    return elements


def build_appendix(targets: list) -> list:
    elements = [Paragraph("Appendix — Discovered Targets", HEADING1)]
    if not targets:
        elements.append(Paragraph("No targets discovered via automated tools.", BODY))
        return elements
    data = [["Host", "Port", "Protocol", "Service", "State"]] + [
        [t["host"], str(t["port"] or ""), t["protocol"], t["service"], t["state"]]
        for t in targets
    ]
    table = Table(data, colWidths=[4 * cm, 2 * cm, 2.5 * cm, 4 * cm, 2.5 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f8f8")]),
        ("FONTSIZE",   (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)
    return elements
