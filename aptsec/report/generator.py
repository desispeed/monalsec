from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate
from aptsec.models import get_engagement, list_findings, list_targets
from aptsec.report.template import (
    build_cover, build_executive_summary,
    build_findings_section, build_appendix,
)


def generate_pdf(conn, engagement_id: int, output_path: str) -> None:
    eng = get_engagement(conn, engagement_id)
    if not eng:
        raise ValueError(f"Engagement #{engagement_id} not found.")

    findings = list_findings(conn, engagement_id)
    targets = list_targets(conn, engagement_id)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2.5 * 28.35,
        leftMargin=2.5 * 28.35,
        topMargin=2.5 * 28.35,
        bottomMargin=2.5 * 28.35,
    )

    story = []
    story += build_cover(eng)
    story += build_executive_summary(findings)
    story += build_findings_section(findings)
    story += build_appendix(targets)

    doc.build(story)
