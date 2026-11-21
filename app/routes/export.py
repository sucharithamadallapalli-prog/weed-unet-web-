
from flask import Blueprint, Response
from flask_login import login_required, current_user
from app.models import Analysis
from app.services.report_service import analyses_to_csv

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

bp = Blueprint("export", __name__)


@bp.route("/export/csv")
@login_required
def csv_export():
    rows = Analysis.query.filter_by(
        user_id=current_user.id
    ).order_by(Analysis.created_at).all()

    return Response(
        analyses_to_csv(rows),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=weed_analyses.csv"
        },
    )


@bp.route("/export/pdf")
@login_required
def pdf_export():
    rows = Analysis.query.filter_by(
        user_id=current_user.id
    ).order_by(Analysis.created_at).all()

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4)
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph("Weed Analysis Report", styles["Title"])
    )
    elements.append(Spacer(1, 20))

    data = [[
        "ID",
        "Field",
        "Weed Coverage (%)",
        "Severity",
        "Created At",
    ]]

    for analysis in rows:
        data.append([
            str(analysis.id),
            analysis.field.name if analysis.field else "",
            str(analysis.weed_percent or 0),
            str(analysis.severity or ""),
            (
                analysis.created_at.strftime("%Y-%m-%d %H:%M")
                if analysis.created_at else ""
            ),
        ])

    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.lightgrey]),
    ]))

    elements.append(table)
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    return Response(
        pdf,
        mimetype="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=weed_analyses.pdf"
        },
    )
