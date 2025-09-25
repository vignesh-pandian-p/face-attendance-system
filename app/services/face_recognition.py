import os
from deepface import DeepFace
import numpy as np
from app.models import User, AttendanceLog, Face
from app.extensions import db
import pytz
from datetime import datetime

IST = pytz.timezone("Asia/Kolkata")

def get_known_faces():
    known_faces_paths = []
    known_names = []
    faces = Face.query.all()
    for face in faces:
        known_faces_paths.append(face.image_path)
        known_names.append(face.user.name)
    return known_faces_paths, known_names

def verify_attendance(captured_image_path):
    known_faces_dir = "static/faces"
    try:
        dfs = DeepFace.find(img_path=captured_image_path, db_path=known_faces_dir, model_name='VGG-Face', distance_metric='cosine', enforce_detection=False)
        if dfs and not dfs[0].empty:
            # The result is a list of dataframes. We are interested in the first one.
            df = dfs[0]
            if not df.empty:
                # Get the identity of the best match
                identity = df.iloc[0]['identity']
                # The identity is the path to the image. We need to extract the user name from it.
                # The image path is like 'static/faces/1_Vignesh Pandian.jpg'
                # We can get the user id from the start of the filename.
                user_id = os.path.basename(identity).split('_')[0]
                user = User.query.get(user_id)
                if user:
                    return user.name
    except Exception as e:
        print(f"Error in DeepFace.find: {e}")
    return "Unknown"


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
