import os
import face_recognition
import numpy as np
from app.models import User, AttendanceLog, Face
from app.extensions import db
from datetime import datetime

def get_known_faces():
    known_encodings = []
    known_names = []
    faces = Face.query.all()
    for face in faces:
        # Convert the binary encoding back to a numpy array
        encoding = np.frombuffer(face.encoding, dtype=np.float64)
        known_encodings.append(encoding)
        known_names.append(face.user.name)
    return known_encodings, known_names

def mark_attendance(user_name):
    user = User.query.filter_by(name=user_name).first()
    if user:
        # Check if attendance has already been marked for this user today
        today = datetime.utcnow().date()
        existing_log = AttendanceLog.query.filter(
            AttendanceLog.user_id == user.id,
            db.func.date(AttendanceLog.timestamp) == today
        ).first()

        if not existing_log:
            new_log = AttendanceLog(user_id=user.id)
            db.session.add(new_log)
            db.session.commit()
