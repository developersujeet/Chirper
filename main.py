from flask import Flask, render_template, request, jsonify
import face_recognition
import numpy as np
import os
import base64

app = Flask(__name__)

# Store known faces and their names
known_face_encodings = []
known_face_names = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    # Get the image from the POST request
    image_file = request.files['image']
    image_path = os.path.join('uploads', image_file.filename)
    image_file.save(image_path)

    # Load the image and get the face encoding
    image = face_recognition.load_image_file(image_path)
    face_encoding = face_recognition.face_encodings(image)

    if face_encoding:
        # Store the encoding and label it with the user's name
        known_face_encodings.append(face_encoding[0])
        known_face_names.append(image_file.filename.split('.')[0])  # Use the file name as the user's name
        
        return jsonify({"message": "Face uploaded and stored successfully!"}), 200
    else:
        return jsonify({"message": "No face detected!"}), 400

@app.route('/check_face', methods=['POST'])
def check_face():
    # Get the base64 image data from the client
    data = request.json['image']
    image_data = base64.b64decode(data)
    
    # Load the image and check for faces
    img_array = np.frombuffer(image_data, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    face_encoding = face_recognition.face_encodings(img)

    if face_encoding:
        results = face_recognition.compare_faces(known_face_encodings, face_encoding[0])
        
        if True in results:
            return jsonify({"message": "Access granted"}), 200
        else:
            return jsonify({"message": "Access denied"}), 403
    else:
        return jsonify({"message": "No face detected!"}), 400

if __name__ == '__main__':
    app.run(debug=True)
