from datetime import datetime
from extensions import db

class Search(db.Model):
    __tablename__ = "searches"
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(255), nullable=False)
    searched_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Search {self.city_name} @ {self.searched_at}>"
