from flask import Flask, render_template_string, Response
import cv2

app = Flask(__name__)
camera = cv2.VideoCapture(0)  # Open webcam

def generate_frames():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

            _, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()

            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Face Detection</title>
    <style>
        body {
            text-align: center;
            font-family: Arial, sans-serif;
            background: #222;
            color: white;
        }
        #video_feed {
            border-radius: 10px;
            width: 640px;
            height: 480px;
            border: 3px solid white;
        }
    </style>
</head>
<body>
    <h1>Face Detection App</h1>
    <img id="video_feed" src="{{ url_for('video_feed') }}" alt="Live Feed">
    <script>
        console.log("Face Detection Running...");
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(html_code)

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    app.run(debug=True)