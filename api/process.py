from flask import Flask, request, jsonify
import cv2
import dlib
import numpy as np
import math
from PIL import Image
import io

app = Flask(__name__)

landmark_predictor_path = "shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(landmark_predictor_path)

def shape_to_np(shape):
    coords = np.zeros((68, 2), dtype=int)
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords

def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

@app.route("/process", methods=["POST"])
def process_image():
    if 'image' not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada"}), 400

    file = request.files["image"]
    image = Image.open(file.stream)
    image = np.array(image)
    
    if len(image.shape) == 3:  # Verificar se é colorida
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    faces = detector(gray, 1)
    if len(faces) == 0:
        return jsonify({"error": "Nenhuma face detectada"}), 400

    for face in faces:
        shape = predictor(gray, face)
        landmarks = shape_to_np(shape)

        chin = landmarks[8]
        nose_tip = landmarks[33]
        left_jaw = landmarks[0]
        right_jaw = landmarks[16]

        face_width = euclidean_distance(left_jaw, right_jaw)
        face_height = euclidean_distance(chin, nose_tip)

    return jsonify({
        "face_width": f"{face_width:.2f}px",
        "face_height": f"{face_height:.2f}px"
    })

# Handler para a Vercel
app.run = app
