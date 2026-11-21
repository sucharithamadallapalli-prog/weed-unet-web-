
import os
import uuid
import traceback

from flask import (
    Blueprint, render_template, request, flash,
    redirect, url_for, current_app, send_from_directory,
    session
)
from flask_login import current_user
from werkzeug.utils import secure_filename

from app import db
from app.models.analysis import Analysis

bp = Blueprint("analysis", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "tif", "tiff"}
VISITOR_FREE_ANALYSES = 5


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


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

    folders = {
        "originals": os.path.join(base, "originals"),
        "masks": os.path.join(base, "masks"),
        "results": os.path.join(base, "results"),
    }

    for folder in folders.values():
        os.makedirs(folder, exist_ok=True)

    return folders


def get_visitor_analyses_remaining():
    if "visitor_analyses_remaining" not in session:
        session["visitor_analyses_remaining"] = VISITOR_FREE_ANALYSES

    return session["visitor_analyses_remaining"]


def get_weed_recommendation(coverage):

    if coverage < 10:
        return {
            "severity": "Low",
            "methods": [
                "Remove isolated weeds manually.",
                "Monitor the field regularly.",
                "Use mulching where suitable."
            ]
        }

    elif coverage < 30:
        return {
            "severity": "Medium",
            "methods": [
                "Perform hand weeding near crop plants.",
                "Use shallow hoeing between crop rows.",
                "Check for weed regrowth."
            ]
        }

    elif coverage < 60:
        return {
            "severity": "High",
            "methods": [
                "Consider mechanical weeding where crop spacing allows.",
                "Remove remaining weeds manually near crops.",
                "Use an integrated weed-management approach."
            ]
        }

    else:
        return {
            "severity": "Very High",
            "methods": [
                "Inspect the field and identify the weed species.",
                "Plan suitable mechanical or manual weed control.",
                "Consult an agricultural expert about suitable control methods."
            ]
        }


@bp.route("/analysis", methods=["GET", "POST"])
def analysis():

    is_logged_in = current_user.is_authenticated

    # Check user free trial
    if is_logged_in:

        if (
            current_user.free_trial_enabled
            and current_user.free_analyses_remaining <= 0
        ):
            flash(
                "Your 5 free analyses have been used.",
                "error"
            )
            return redirect(url_for("dashboard.dashboard"))

        remaining = current_user.free_analyses_remaining
        trial_enabled = current_user.free_trial_enabled

    else:

        remaining = get_visitor_analyses_remaining()
        trial_enabled = True

        if remaining <= 0:
            flash(
                "You have used all 5 visitor free analyses. Please register or log in.",
                "error"
            )
            return redirect(url_for("auth.register"))

    if request.method == "GET":
        return render_template(
            "analysis.html",
            free_analyses_remaining=remaining,
            trial_enabled=trial_enabled,
        )

    uploaded = request.files.get("image")

    if not uploaded or not uploaded.filename:
        flash("Please select a field image.", "error")
        return redirect(url_for("analysis.analysis"))

    if not allowed_file(uploaded.filename):
        flash("Upload a PNG, JPG, JPEG, or TIFF image.", "error")
        return redirect(url_for("analysis.analysis"))

    safe_name = secure_filename(uploaded.filename)
    extension = safe_name.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{extension}"

    folders = get_upload_dirs()

    original_path = os.path.join(folders["originals"], filename)
    mask_path = os.path.join(folders["masks"], filename)
    result_path = os.path.join(folders["results"], filename)

    try:
        uploaded.save(original_path)

        # Run U-Net prediction
        from app.services.unet_predict import predict_image

        prediction = predict_image(
            original_path,
            mask_path,
            result_path
        )

        # Get coverage and confidence from model
        coverage = float(prediction["weed_coverage"])
        confidence = float(prediction["weed_confidence"])

        # Get weed severity and removal methods
        recommendation = get_weed_recommendation(coverage)

        # Store analysis in database
        record = Analysis(
            original=filename,
            mask=filename,
            overlay=filename,
            weed_percent=coverage,
            severity=recommendation["severity"].lower(),
            user_id=current_user.id if is_logged_in else None,
            field_id=None
        )

        # Reduce free trial only after successful prediction
        if is_logged_in:
            if current_user.free_trial_enabled:
                current_user.free_analyses_remaining -= 1
        else:
            session["visitor_analyses_remaining"] = remaining - 1

        db.session.add(record)
        db.session.commit()

        # Redirect visitor after fifth successful analysis
        if (
            not is_logged_in
            and session["visitor_analyses_remaining"] <= 0
        ):
            flash(
                "Your 5 free analyses are complete! Please register or log in.",
                "success"
            )
            return redirect(url_for("auth.register"))

        # Display analysis results
        return render_template(
            "analysis_result.html",
            original=filename,
            mask=filename,
            result=filename,
            weed_coverage=coverage,
            weed_confidence=confidence,
            severity=recommendation["severity"],
            weed_methods=recommendation["methods"]
        )

    except Exception as error:

        db.session.rollback()

        if not is_logged_in:
            session["visitor_analyses_remaining"] = remaining

        traceback.print_exc()
        current_app.logger.exception("Weed analysis failed")

        for path in (original_path, mask_path, result_path):
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

        flash(
            f"Analysis failed: {type(error).__name__}: {error}",
            "error"
        )

        return redirect(url_for("analysis.analysis"))


@bp.route("/uploads/<kind>/<filename>")
def uploads(kind, filename):

    folders = get_upload_dirs()

    if kind not in folders:
        return "Invalid upload type", 404

    return send_from_directory(folders[kind], filename)
