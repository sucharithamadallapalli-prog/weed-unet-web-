from app import db

class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    crop = db.Column(db.String(80))
    area_ha = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    analyses = db.relationship("Analysis", backref="field", lazy=True)
