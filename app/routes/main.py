from flask import Blueprint, render_template, request, redirect, send_file
from flask import Blueprint, render_template, request, redirect, send_file
from flask import Blueprint, render_template, request, redirect, url_for, send_file
import os
import cv2
import face_recognition
from datetime import datetime
from app.services.face_recognition import get_known_faces, mark_attendance
from app.extensions import db
from app.models import User, AttendanceLog

main_bp = Blueprint('main', __name__)

UPLOAD_FOLDER = 'static/faces'
LOG_FOLDER = 'logs'  # Folder to store log files

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        department = request.form.get('department')
        section = request.form.get('section')
        current_year = request.form.get('current_year', type=int)

        # Check if user already exists
        if User.query.filter_by(name=name).first():
            # Handle user already exists error, maybe flash a message
            return redirect(url_for('main.register'))

        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Display instructions on the frame
            cv2.putText(frame, "Press 'S' to save, 'Q' to quit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Capture Face", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                image_path = os.path.join(UPLOAD_FOLDER, f"{name}.jpg")
                cv2.imwrite(image_path, frame)

                # Save user to database
                new_user = User(
                    name=name,
                    image_path=image_path,
                    department=department,
                    section=section,
                    current_year=current_year
                )
                db.session.add(new_user)
                db.session.commit()

                break
            elif key == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        return redirect(url_for('main.index'))
    return render_template('register.html')

from app.services.face_recognition import get_known_faces, mark_attendance

@main_bp.route('/attendance')
def attendance():
    known_encodings, known_names = get_known_faces()
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]
                mark_attendance(name)

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

        cv2.imshow('Attendance', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return redirect(url_for('main.index'))

from app.models import AttendanceLog

import io
import csv
from flask import Response

import openpyxl

@main_bp.route('/import', methods=['GET', 'POST'])
def import_excel():
    if request.method == 'POST':
        file = request.files['excel_file']
        if file:
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active
            for row in sheet.iter_rows(min_row=2, values_only=True):
                name, department, section, current_year = row
                if not User.query.filter_by(name=name).first():
                    # For now, image_path is a placeholder.
                    # The user will need to capture the face separately.
                    user = User(
                        name=name,
                        department=department,
                        section=section,
                        current_year=current_year,
                        image_path=f"static/faces/{name}.jpg" # Placeholder
                    )
                    db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.dashboard'))
    return render_template('import_excel.html')

@main_bp.route('/dashboard')
def dashboard():
    logs = AttendanceLog.query.order_by(AttendanceLog.timestamp.desc()).all()
    return render_template('dashboard.html', logs=logs)

@main_bp.route('/download/attendance.csv')
def download_attendance_csv():
    logs = AttendanceLog.query.all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write headers
    writer.writerow(['ID', 'User Name', 'Timestamp'])

    # Write data
    for log in logs:
        writer.writerow([log.id, log.user.name, log.timestamp.strftime('%Y-%m-%d %H:%M:%S')])

    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=attendance.csv"}
    )
