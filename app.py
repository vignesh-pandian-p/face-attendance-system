from flask import Flask, render_template, request, redirect, send_file
import os
import cv2
import face_recognition
import pandas as pd
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'static/faces'
LOG_FOLDER = 'logs'  # Folder to store log files

# Create folders if not exist
for folder in [UPLOAD_FOLDER, LOG_FOLDER]:
    os.makedirs(folder, exist_ok=True)

def get_known_faces():
    encodings = []
    names = []
    for file in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, file)
        img = face_recognition.load_image_file(path)
        enc = face_recognition.face_encodings(img)
        if enc:
            encodings.append(enc[0])
            names.append(os.path.splitext(file)[0])
    return encodings, names

def mark_attendance(name, filepath):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
    else:
        df = pd.DataFrame(columns=["Name", "Time", "Date"])

    # Only mark once per student per session
    if not ((df["Name"] == name) & (df["Date"] == date)).any():
        df.loc[len(df)] = [name, time, date]
        df.to_csv(filepath, index=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Press S to Save, Q to Quit", frame)
            key = cv2.waitKey(1)
            if key == ord('s'):
                filepath = os.path.join(UPLOAD_FOLDER, f"{name}.jpg")
                cv2.imwrite(filepath, frame)
                break
            elif key == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        return redirect('/')
    return render_template('register.html')

@app.route('/attendance')
def attendance():
    known_encodings, known_names = get_known_faces()
    cap = cv2.VideoCapture(0)
    seen = set()

    # Create unique log file per session
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H-%M")
    log_filename = f"attendance_{date_str}_{time_str}.csv"
    log_path = os.path.join(LOG_FOLDER, log_filename)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, locations)
        for encoding, location in zip(encodings, locations):
            matches = face_recognition.compare_faces(known_encodings, encoding)
            if True in matches:
                idx = matches.index(True)
                name = known_names[idx]
                if name not in seen:
                    mark_attendance(name, log_path)
                    seen.add(name)
                top, right, bottom, left = location
                cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)
        cv2.imshow("Press Q to Quit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return redirect('/')

@app.route('/download-latest')
def download_latest():
    files = [f for f in os.listdir(LOG_FOLDER) if f.endswith('.csv')]
    if not files:
        return "No attendance logs found."
    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(LOG_FOLDER, f)))
    return send_file(os.path.join(LOG_FOLDER, latest_file), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
