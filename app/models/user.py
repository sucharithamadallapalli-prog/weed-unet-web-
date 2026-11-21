from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    free_analyses_remaining = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    # True only for newly registered users who receive the free trial.
    # Existing accounts will have False and retain unlimited access.
    free_trial_enabled = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    fields = db.relationship("Field", backref="owner", lazy=True)
    analyses = db.relationship("Analysis", backref="user", lazy=True)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)