from flask import Flask, request, render_template, send_file, jsonify
import cv2
import numpy as np
from ultralytics import YOLO
import io
from PIL import Image

app = Flask(__name__)

# Load YOLOv8n model
model = YOLO('../app/Model/yolov8n.pt')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    image_bytes = image_file.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Perform detection
    results = model(img)

    bbox_coords = []

    # Draw bounding boxes on the image
    for result in results[0].boxes:
        if result is not None:
            x1, y1, x2, y2 = result.xyxy[0]
            confidence = result.conf[0]
            bbox_coords.append((int(x1), int(y1), int(x2), int(y2), float(confidence)))
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(img, f'{confidence:.2f}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

    print("Bounding Box Coordinates:", bbox_coords)

    # Convert the image to PIL format
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    # Save the image to a bytes buffer
    buf = io.BytesIO()
    img_pil.save(buf, format='JPEG')
    buf.seek(0)

    return send_file(buf, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
