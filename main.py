from flask import Flask, request, Response, render_template_string
import cv2
import numpy as np

app = Flask(__name__)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

@app.route("/")
def index():
    return render_template_string(html_code)

@app.route("/detect_faces", methods=["POST"])
def detect_faces():
    try:
        file = request.files["image"].read()
        np_img = np.frombuffer(file, np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        _, buffer = cv2.imencode(".jpg", frame)
        return Response(buffer.tobytes(), content_type="image/jpeg")

    except Exception as e:
        return f"Error: {str(e)}", 500

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Face Detection</title>
    <style>
        body { text-align: center; font-family: Arial, sans-serif; background: #222; color: white; }
        video, img { width: 100%; max-width: 640px; border: 3px solid white; border-radius: 10px; }
    </style>
</head>
<body>
    <h1>Face Detection App</h1>
    <video id="video" autoplay></video>
    <img id="canvas">
    <script>
        const video = document.getElementById("video");
        const canvas = document.getElementById("canvas");

        async function startCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                video.srcObject = stream;
            } catch (err) {
                console.error("Error accessing webcam:", err);
            }
        }

        async function captureAndSendFrame() {
            const canvasElem = document.createElement("canvas");
            const ctx = canvasElem.getContext("2d");

            canvasElem.width = video.videoWidth;
            canvasElem.height = video.videoHeight;
            ctx.drawImage(video, 0, 0, canvasElem.width, canvasElem.height);

            canvasElem.toBlob(async (blob) => {
                const formData = new FormData();
                formData.append("image", blob, "frame.jpg");

                try {
                    const response = await fetch("/detect_faces", { method: "POST", body: formData });
                    const blobResp = await response.blob();
                    const imgURL = URL.createObjectURL(blobResp);
                    canvas.src = imgURL;
                } catch (err) {
                    console.error("Face detection error:", err);
                }
            }, "image/jpeg");
        }

        video.addEventListener("play", () => setInterval(captureAndSendFrame, 500));
        startCamera();
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)