from app import create_app, db
from app.models import User, Class, AttendanceLog
from datetime import datetime

app = create_app()

with app.app_context():
    # Create a class
    if not Class.query.first():
        new_class = Class(department='CSE', section='A', year=1, advisor='Dr. Smith')
        db.session.add(new_class)
        db.session.commit()
    else:
        new_class = Class.query.first()

    # Create a student
    if not User.query.first():
        new_student = User(name='John Doe', class_id=new_class.id)
        db.session.add(new_student)
        db.session.commit()
    else:
        new_student = User.query.first()

    # Create some attendance logs
    if not AttendanceLog.query.first():
        log1 = AttendanceLog(user_id=new_student.id, timestamp=datetime(2024, 8, 1, 9, 5, 0))
        log2 = AttendanceLog(user_id=new_student.id, timestamp=datetime(2024, 8, 2, 9, 2, 0))
        log3 = AttendanceLog(user_id=new_student.id, timestamp=datetime(2024, 9, 1, 9, 1, 0))
        db.session.add_all([log1, log2, log3])
        db.session.commit()

    print("Dummy data added.")
