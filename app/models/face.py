from app.extensions import db

class Face(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    encoding = db.Column(db.LargeBinary, nullable=False)

    user = db.relationship('User', backref=db.backref('faces', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<Face {self.id} for User {self.user.name}>'
