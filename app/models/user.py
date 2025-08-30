from app.extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    section = db.Column(db.String(100), nullable=True)
    current_year = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<User {self.name}>'
