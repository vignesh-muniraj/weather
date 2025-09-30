
from extensions import db
from datetime import datetime

class Search(db.Model):
    __tablename__ = "searches"
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(255), nullable=False)
    searched_at = db.Column(db.DateTime, default=datetime.utcnow)
