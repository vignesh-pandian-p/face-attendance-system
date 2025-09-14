from flask import Blueprint, render_template, request, redirect, url_for, send_file, Response
import os
import cv2
import io
import csv
import openpyxl
import numpy as np
from deepface import DeepFace
from datetime import datetime
import pytz
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

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        class_id = request.form.get('class_id', type=int)

        if User.query.filter_by(name=name).first():
            return redirect(url_for('main.register'))

        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.putText(frame, "Press 'S' to save, 'Q' to quit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Capture Face", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                # Save user first to get an ID
                new_user = User(
                    name=name,
                    class_id=class_id
                )
                db.session.add(new_user)
                db.session.commit()

                # Now save the face
                image_path = os.path.join(UPLOAD_FOLDER, f"{new_user.id}_{name}.jpg")
                cv2.imwrite(image_path, frame)

                new_face = Face(
                    user_id=new_user.id,
                    image_path=image_path
                )
                db.session.add(new_face)
                db.session.commit()

                break
            elif key == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        return redirect(url_for('main.index'))
    classes = Class.query.all()
    return render_template('register.html', classes=classes)


def mark_attendance(name):
    user = User.query.filter_by(name=name).first()
    if user:
        # Check if already marked today
        today = date.today()
        log = AttendanceLog.query.filter(
            AttendanceLog.user_id == user.id,
            db.func.date(AttendanceLog.timestamp) == today
        ).first()
        if not log:
            new_log = AttendanceLog(user_id=user.id)
            db.session.add(new_log)
            db.session.commit()

@main_bp.route('/attendance')
def attendance():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        try:
            dfs = DeepFace.find(img_path=frame, db_path=UPLOAD_FOLDER, enforce_detection=False)
            for df in dfs:
                if not df.empty:
                    identity = df.iloc[0]['identity']
                    user_id = int(os.path.basename(identity).split('_')[0])
                    user = User.query.get(user_id)
                    if user:
                        mark_attendance(user.name)
                        # Draw rectangle and name on the frame
                        # This part is tricky as DeepFace.find does not return face locations directly
                        # For now, we'll just mark attendance without drawing on the frame
        except Exception as e:
            print(e)
            # Handle case where no face is detected or other errors
            pass

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
                name, class_id = row
                if not User.query.filter_by(name=name).first():
                    # For now, image_path is a placeholder.
                    # The user will need to capture the face separately.
                    user = User(
                        name=name,
                        class_id=class_id,
                        image_path=f"static/faces/{name}.jpg" # Placeholder
                    )
                    db.session.add(user)
            db.session.commit()
            return redirect(url_for('main.dashboard'))
    return render_template('import_excel.html')

@main_bp.route('/add_face/<int:student_id>', methods=['GET'])
def add_face(student_id):
    student = User.query.get_or_404(student_id)
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
                image_path=image_path
            )
            db.session.add(new_face)
            db.session.commit()

            break
        elif key == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    return redirect(url_for('main.edit_student', student_id=student_id))

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
        student.class_id = request.form['class_id']
        db.session.commit()
        return redirect(url_for('main.class_detail', class_id=student.class_id))
    classes = Class.query.all()
    return render_template('edit_student.html', student=student, classes=classes)

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
    class_ = Class.query.get_or_404(class_id)
    return render_template('class_detail.html', class_=class_)

@main_bp.route('/dashboard')
def dashboard():
    logs = AttendanceLog.query.order_by(AttendanceLog.timestamp.desc()).all()
    return render_template('dashboard.html', logs=logs)

from app.services.pdf_generator import generate_class_report_pdf
from flask import Response
from datetime import date

@main_bp.route('/report/class/<int:class_id>/daily')
def daily_class_report(class_id):
    class_ = Class.query.get_or_404(class_id)
    students = class_.students
    today = date.today()
    attendance_logs = AttendanceLog.query.filter(
        AttendanceLog.user_id.in_([student.id for student in students]),
        db.func.date(AttendanceLog.timestamp) == today
    ).all()

    pdf_content = generate_class_report_pdf(class_, students, attendance_logs)

    return Response(pdf_content,
                    mimetype='application/pdf',
                    headers={'Content-Disposition': f'attachment;filename=daily_report_{class_.department}_{today}.pdf'})

from app.services.pdf_generator import generate_monthly_class_report_pdf

@main_bp.route('/report/class/<int:class_id>/monthly')
def monthly_class_report(class_id):
    class_ = Class.query.get_or_404(class_id)
    students = class_.students
    month = request.args.get('month', date.today().month, type=int)
    year = request.args.get('year', date.today().year, type=int)

    attendance_logs = AttendanceLog.query.filter(
        AttendanceLog.user_id.in_([student.id for student in students]),
        db.extract('month', AttendanceLog.timestamp) == month,
        db.extract('year', AttendanceLog.timestamp) == year
    ).all()

    pdf_content = generate_monthly_class_report_pdf(class_, students, attendance_logs, month, year)

    return Response(pdf_content,
                    mimetype='application/pdf',
                    headers={'Content-Disposition': f'attachment;filename=monthly_report_{class_.department}_{month}_{year}.pdf'})

from app.services.pdf_generator import generate_monthly_student_report_pdf, generate_yearly_student_report_pdf

@main_bp.route('/report/student/<int:student_id>/monthly')
def monthly_student_report(student_id):
    student = User.query.get_or_404(student_id)
    month = request.args.get('month', date.today().month, type=int)
    year = request.args.get('year', date.today().year, type=int)

    attendance_logs = AttendanceLog.query.filter(
        AttendanceLog.user_id == student_id,
        db.extract('month', AttendanceLog.timestamp) == month,
        db.extract('year', AttendanceLog.timestamp) == year
    ).all()

    pdf_content = generate_monthly_student_report_pdf(student, attendance_logs, month, year)

    return Response(pdf_content,
                    mimetype='application/pdf',
                    headers={'Content-Disposition': f'attachment;filename=monthly_report_{student.name}_{month}_{year}.pdf'})

@main_bp.route('/report/student/<int:student_id>/yearly')
def yearly_student_report(student_id):
    student = User.query.get_or_404(student_id)
    year = request.args.get('year', date.today().year, type=int)

    attendance_logs = AttendanceLog.query.filter(
        AttendanceLog.user_id == student_id,
        db.extract('year', AttendanceLog.timestamp) == year
    ).all()

    pdf_content = generate_yearly_student_report_pdf(student, attendance_logs, year)

    return Response(pdf_content,
                    mimetype='application/pdf',
                    headers={'Content-Disposition': f'attachment;filename=yearly_report_{student.name}_{year}.pdf'})
