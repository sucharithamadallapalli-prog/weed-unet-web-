
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user

from app import db
from app.models.user import User

bp = Blueprint("auth", __name__)


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    # Send visitors directly to the five-analysis free trial.
    return redirect(url_for("analysis.analysis"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Enter both a username and password.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must contain at least 6 characters.", "error")
            return render_template("register.html")

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            flash("That username is already registered.", "error")
            return render_template("register.html")

        # Newly registered accounts receive five free analyses.
        user = User(
            username=username,
            free_analyses_remaining=5,
            free_trial_enabled=True
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash(
            "Registration successful! You have 5 free analyses. Please log in.",
            "success"
        )

        return redirect(url_for("auth.login"))

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)

            next_page = request.args.get("next")

            if (
                next_page
                and next_page.startswith("/")
                and not next_page.startswith("//")
            ):
                return redirect(next_page)

            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
