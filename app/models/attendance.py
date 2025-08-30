from app.extensions import db
from datetime import datetime

class AttendanceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('logs', lazy=True))

    def __repr__(self):
        return f'<AttendanceLog {self.user.name} at {self.timestamp}>'
