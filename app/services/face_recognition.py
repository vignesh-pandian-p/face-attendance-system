import os
import face_recognition
import numpy as np
from app.models import User, AttendanceLog, Face
from app.extensions import db
import pytz
from datetime import datetime

IST = pytz.timezone("Asia/Kolkata")

def get_known_faces():
    known_encodings = []
    known_names = []
    faces = Face.query.all()
    for face in faces:
        # Convert the string encoding back to a numpy array
        encoding = np.fromstring(face.encoding, sep=',')
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
