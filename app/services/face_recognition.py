import os
import face_recognition
from app.models import User, AttendanceLog
from app.extensions import db
from datetime import datetime

def get_known_faces():
    known_encodings = []
    known_names = []
    users = User.query.all()
    for user in users:
        try:
            image = face_recognition.load_image_file(user.image_path)
            encoding = face_recognition.face_encodings(image)[0]
            known_encodings.append(encoding)
            known_names.append(user.name)
        except (FileNotFoundError, IndexError):
            # Handle cases where image is missing or no face is found
            pass
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
