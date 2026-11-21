
from datetime import datetime
from app import db


class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    original = db.Column(db.String(255), nullable=False)
    mask = db.Column(db.String(255), nullable=False)
    overlay = db.Column(db.String(255), nullable=False)

    weed_percent = db.Column(
        db.Float,
        nullable=False,
        default=0.0
    )

    severity = db.Column(
        db.String(30),
        nullable=False,
        default="low"
    )

    # Anonymous visitors can now have analyses without a user account.
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    field_id = db.Column(
        db.Integer,
        db.ForeignKey("field.id"),
        nullable=True
    )
