from app.extensions import db

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(10), nullable=False)

    users = db.relationship('User', backref='class', lazy=True)

    def __repr__(self):
        return f'<Class {self.year} {self.department} {self.section}>'
