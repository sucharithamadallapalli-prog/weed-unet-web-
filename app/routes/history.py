import os

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    current_app,
    flash,
)
from flask_login import login_required, current_user

from app import db
from app.models import Analysis

bp = Blueprint("history", __name__)


def get_upload_dirs():
    root = os.path.abspath(
        os.path.join(current_app.root_path, "..")
    )

    base = (
        current_app.config.get("UPLOAD_FOLDER")
        or current_app.config.get("UPLOAD_DIR")
        or os.path.join(root, "uploads")
    )

    if not os.path.isabs(base):
        base = os.path.join(root, base)

    return {
        "originals": os.path.join(base, "originals"),
        "masks": os.path.join(base, "masks"),
        "results": os.path.join(base, "results"),
    }


@bp.route("/history")
@login_required
def index():
    rows = (
        Analysis.query
        .filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )

    return render_template("history.html", rows=rows)


@bp.route("/history/<int:aid>/delete", methods=["POST"])
@login_required
def delete(aid):
    analysis_record = Analysis.query.filter_by(
        id=aid,
        user_id=current_user.id,
    ).first_or_404()

    folders = get_upload_dirs()

    files_to_delete = [
        ("originals", analysis_record.original),
        ("masks", analysis_record.mask),
        ("results", analysis_record.overlay),
    ]

    for folder_name, filename in files_to_delete:
        if not filename:
            continue

        file_path = os.path.join(
            folders[folder_name],
            filename,
        )

        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except OSError:
            current_app.logger.warning(
                "Could not delete analysis file: %s",
                file_path,
            )

    db.session.delete(analysis_record)
    db.session.commit()

    flash(
        "Analysis record deleted successfully.",
        "success",
    )

    return redirect(url_for("history.index"))
