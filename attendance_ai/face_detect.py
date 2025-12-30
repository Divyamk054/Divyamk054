import cv2
import csv
from datetime import datetime

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

prev_center = None
live = False
attendance_marked = False

name = input("Enter your name: ")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        center = (x + w // 2, y + h // 2)

        if prev_center is not None:
            movement = abs(center[0] - prev_center[0]) + abs(center[1] - prev_center[1])
            if movement > 15:
                live = True

        prev_center = center

        if live and not attendance_marked:
            with open("attendance.csv", "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            attendance_marked = True
            print("Attendance marked successfully!")

        color = (0, 255, 0) if live else (0, 0, 255)
        text = "LIVE - Attendance Marked" if attendance_marked else ("LIVE" if live else "NOT LIVE")

        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow("Fraud-Proof Attendance System - Press Q to Exit", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
