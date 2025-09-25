from flask import Blueprint, render_template, request, redirect, send_file
from flask import Blueprint, render_template, request, redirect, send_file
from flask import Blueprint, render_template, request, redirect, url_for, send_file
import os
import cv2
from datetime import datetime
import pytz
from app.services.face_recognition import verify_attendance, mark_attendance
from app.extensions import db
from app.models import User, AttendanceLog, Class

main_bp = Blueprint('main', __name__)

IST = pytz.timezone("Asia/Kolkata")

UPLOAD_FOLDER = 'static/faces'
LOG_FOLDER = 'logs'  # Folder to store log files

@main_bp.route('/')
def index():
    return render_template('index.html')

import numpy as np
from app.models import Face


@main_bp.route('/add_face/<int:student_id>', methods=['GET', 'POST'])
def add_face(student_id):
    student = User.query.get_or_404(student_id)
    if request.method == 'POST':
        # This part will be triggered by a form, but for now, we'll just capture the face
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.putText(frame, f"Adding face for {student.name}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'S' to save, 'Q' to quit", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Add Face", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                image_path = os.path.join(UPLOAD_FOLDER, f"{student.id}_{student.name}_{len(student.faces) + 1}.jpg")
                cv2.imwrite(image_path, frame)

                new_face = Face(
                    user_id=student.id,
                    image_path=image_path,
                    encoding=""  # Not storing encoding anymore
                )
                db.session.add(new_face)
                db.session.commit()

                break
            elif key == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        return redirect(url_for('main.class_detail', class_id=student.class_id))

    return render_template('add_face.html', student=student)

@main_bp.route('/classes')
def classes():
    all_classes = Class.query.all()
    return render_template('classes.html', classes=all_classes)

@main_bp.route('/add_class', methods=['GET', 'POST'])
def add_class():
    if request.method == 'POST':
        department = request.form['department']
        section = request.form['section']
        year = request.form['year']
        advisor = request.form['advisor']
        new_class = Class(department=department, section=section, year=year, advisor=advisor)
        db.session.add(new_class)
        db.session.commit()
        return redirect(url_for('main.classes'))
    return render_template('add_class.html')

@main_bp.route('/class/<int:class_id>')
def class_detail(class_id):
    class_obj = Class.query.get_or_404(class_id)
    return render_template('class_detail.html', class_obj=class_obj)

@main_bp.route('/delete_student/<int:student_id>', methods=['GET'])
def delete_student(student_id):
    student = User.query.get_or_404(student_id)
    class_id = student.class_id
    # Delete associated face images
    for face in student.faces:
        if os.path.exists(face.image_path):
            os.remove(face.image_path)

    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('main.class_detail', class_id=class_id))

@main_bp.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    student = User.query.get_or_404(student_id)
    if request.method == 'POST':
        student.name = request.form['name']
        db.session.commit()
        return redirect(url_for('main.class_detail', class_id=student.class_id))
    return render_template('edit_student.html', student=student)

@main_bp.route('/add_student/<int:class_id>', methods=['GET', 'POST'])
def add_student(class_id):
    if request.method == 'POST':
        name = request.form['name']
        new_user = User(name=name, class_id=class_id)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.add_face', student_id=new_user.id))
    return render_template('add_student.html', class_id=class_id)

@main_bp.route('/attendance')
def attendance():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # For now, we'll just use a temporary file to store the captured frame
        temp_image_path = "temp_capture.jpg"
        cv2.imwrite(temp_image_path, frame)

        # We need to find the faces in the frame and then verify them
        # This part is a bit tricky with deepface as it is designed for single face verification
        # For now, let's just try to verify the whole frame
        name = verify_attendance(temp_image_path)

        if name != "Unknown":
            mark_attendance(name)

        # We can still display the frame with the recognized name
        cv2.putText(frame, name, (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
        cv2.imshow('Attendance', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    # Clean up the temporary file
    if os.path.exists(temp_image_path):
        os.remove(temp_image_path)

    return redirect(url_for('main.index'))

@main_bp.route('/dashboard')
def dashboard():
    total_classes = Class.query.count()

    classes = Class.query.all()
    class_names = [f"{c.department} {c.year} {c.section}" for c in classes]
    student_counts = [len(c.students) for c in classes]

    today = datetime.utcnow().date()
    present_counts = []
    absent_counts = []

    for c in classes:
        student_ids = [s.id for s in c.students]
        present_count = AttendanceLog.query.filter(
            AttendanceLog.user_id.in_(student_ids),
            db.func.date(AttendanceLog.timestamp) == today
        ).count()
        present_counts.append(present_count)
        absent_counts.append(len(student_ids) - present_count)

    logs = AttendanceLog.query.order_by(AttendanceLog.timestamp.desc()).all()

    return render_template(
        'dashboard.html',
        logs=logs,
        total_classes=total_classes,
        class_names=class_names,
        student_counts=student_counts,
        present_counts=present_counts,
        absent_counts=absent_counts
    )

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

from flask import make_response
from weasyprint import HTML
from datetime import datetime

@main_bp.route('/reports', methods=['GET'])
def reports():
    students = User.query.all()
    return render_template('reports.html', students=students, now=datetime.now())

@main_bp.route('/generate_report', methods=['POST'])
def generate_report():
    report_type = request.form.get('report_type')
    month = int(request.form.get('month'))
    year = int(request.form.get('year'))
    student_id = request.form.get('student_id')

    if report_type == 'monthly':
        logs = AttendanceLog.query.filter(
            db.extract('month', AttendanceLog.timestamp) == month,
            db.extract('year', AttendanceLog.timestamp) == year
        ).all()
        template = render_template('report_template.html', logs=logs, month=month, year=year, report_type=report_type)
    elif report_type == 'student':
        logs = AttendanceLog.query.filter(
            db.extract('month', AttendanceLog.timestamp) == month,
            db.extract('year', AttendanceLog.timestamp) == year,
            AttendanceLog.user_id == student_id
        ).all()
        student = User.query.get(student_id)
        template = render_template('report_template.html', logs=logs, month=month, year=year, student=student, report_type=report_type)
    else:
        return "Invalid report type", 400

    html = HTML(string=template)
    pdf = html.write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={report_type}_report_{month}_{year}.pdf'

    return response
