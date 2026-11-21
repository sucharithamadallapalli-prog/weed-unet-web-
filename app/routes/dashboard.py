from flask import Blueprint, render_template, session
from flask_login import login_required, current_user

from app.models.field import Field
from app.models.analysis import Analysis

bp = Blueprint("dashboard", __name__)


@bp.route("/dashboard")
@login_required
def dashboard():
    fields = (
        Field.query
        .filter_by(user_id=current_user.id)
        .order_by(Field.id.desc())
        .all()
    )

    analyses = (
        Analysis.query
        .filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .limit(10)
        .all()
    )

    total_fields = len(fields)

    total_analyses = (
        Analysis.query
        .filter_by(user_id=current_user.id)
        .count()
    )

    latest_analysis = analyses[0] if analyses else None

    language = session.get("language", "en")

    return render_template(
        "dashboard.html",
        fields=fields,
        analyses=analyses,
        total_fields=total_fields,
        total_analyses=total_analyses,
        latest_analysis=latest_analysis,
        current_language=language,
    )
from flask import Blueprint, render_template, session
from flask_login import login_required, current_user

from app.models.field import Field
from app.models.analysis import Analysis

bp = Blueprint("dashboard", __name__)


@bp.route("/dashboard")
@login_required
def dashboard():
    fields = (
        Field.query
        .filter_by(user_id=current_user.id)
        .order_by(Field.id.desc())
        .all()
    )

    analyses = (
        Analysis.query
        .filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .limit(10)
        .all()
    )

    total_fields = len(fields)

    total_analyses = (
        Analysis.query
        .filter_by(user_id=current_user.id)
        .count()
    )

    latest_analysis = analyses[0] if analyses else None

    language = session.get("language", "en")

    return render_template(
        "dashboard.html",
        fields=fields,
        analyses=analyses,
        total_fields=total_fields,
        total_analyses=total_analyses,
        latest_analysis=latest_analysis,
        current_language=language,
    )
