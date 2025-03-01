from flask import Flask, request, Response, render_template_string, send_file
import cv2
import numpy as np
import face_recognition
import os

app = Flask(__name__)

# Create a folder to store captured images
if not os.path.exists("captured"):
    os.makedirs("captured")

# Load known faces (replace with your own images)
known_faces = []
known_names = []

def add_known_face(image_path, name):
    image = face_recognition.load_image_file(image_path)
    encoding = face_recognition.face_encodings(image)[0]
    known_faces.append(encoding)
    known_names.append(name)

# Add faces (replace with your own images)
add_known_face("sujeet.jpg", "Sujeet")
add_known_face("tony_stark.jpg", "Tony Stark")

@app.route("/")
def index():
    return render_template_string(html_code)

@app.route("/capture", methods=["POST"])
def capture():
    try:
        file = request.files["image"].read()
        filename = "captured/captured.jpg"

        with open(filename, "wb") as f:
            f.write(file)

        return "Image captured successfully!", 200

    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/detect")
def detect():
    try:
        filename = "captured/captured.jpg"
        if not os.path.exists(filename):
            return "No image captured yet!", 400

        frame = cv2.imread(filename)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_faces, face_encoding)
            name = "Unknown"

            if True in matches:
                matched_idx = matches.index(True)
                name = known_names[matched_idx]

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        processed_filename = "captured/detected.jpg"
        cv2.imwrite(processed_filename, frame)

        return send_file(processed_filename, mimetype="image/jpeg")

    except Exception as e:
        return f"Error: {str(e)}", 500

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Face Recognition</title>
    <style>
        body { text-align: center; font-family: Arial, sans-serif; background: #222; color: white; }
        video, img { width: 100%; max-width: 640px; border: 3px solid white; border-radius: 10px; margin-bottom: 10px; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; background: green; color: white; border: none; }
    </style>
</head>
<body>
    <h1>Face Recognition</h1>
    <video id="video" autoplay></video>
    <br>
    <button onclick="captureImage()">Capture Image</button>
    <button onclick="detectFace()">Detect Face</button>
    <br><br>
    <img id="capturedImage">
    <script>
        const video = document.getElementById("video");
        const capturedImage = document.getElementById("capturedImage");

        async function startCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                video.srcObject = stream;
            } catch (err) {
                console.error("Error accessing webcam:", err);
            }
        }

        async function captureImage() {
            const canvasElem = document.createElement("canvas");
            const ctx = canvasElem.getContext("2d");

            canvasElem.width = video.videoWidth;
            canvasElem.height = video.videoHeight;
            ctx.drawImage(video, 0, 0, canvasElem.width, canvasElem.height);

            canvasElem.toBlob(async (blob) => {
                const formData = new FormData();
                formData.append("image", blob, "captured.jpg");

                try {
                    await fetch("/capture", { method: "POST", body: formData });
                    const imgURL = URL.createObjectURL(blob);
                    capturedImage.src = imgURL;
                } catch (err) {
                    console.error("Capture error:", err);
                }
            }, "image/jpeg");
        }

        async function detectFace() {
            try {
                capturedImage.src = "/detect?" + new Date().getTime();
            } catch (err) {
                console.error("Detection error:", err);
            }
        }

        startCamera();
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)