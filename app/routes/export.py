from flask import Blueprint, Response
from flask_login import login_required, current_user
from app.models import Analysis
from app.services.report_service import analyses_to_csv

bp = Blueprint("export", __name__)

@bp.route("/export/csv")
@login_required
def csv_export():
    rows = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.created_at).all()
    return Response(analyses_to_csv(rows), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=weed_analyses.csv"})
