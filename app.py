from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageFilter, ImageOps
import numpy as np
import os
from io import BytesIO
from ml_model import classify_image

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Convert image to sketch
def convert_to_sketch(image_path):
    # Load image
    img = Image.open(image_path).convert("RGB")
    
    # Convert to grayscale
    gray_img = ImageOps.grayscale(img)
    
    # Invert the grayscale image
    inverted_img = ImageOps.invert(gray_img)
    
    # Blur the inverted image
    blurred_img = inverted_img.filter(ImageFilter.GaussianBlur(radius=10))
    
    # Perform dodging
    def dodge(front, back):
        result = front * 255 / (255 - back)
        result[result > 255] = 255
        result[back == 255] = 255
        return result.astype("uint8")
    
    gray_np = np.array(gray_img)
    blurred_np = np.array(blurred_img)
    sketch_np = dodge(blurred_np, gray_np)
    
    # Convert the result back to an image
    sketch_img = Image.fromarray(sketch_np, mode="L")
    return sketch_img

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        
        # Process the image to convert it to a sketch
        sketch_img = convert_to_sketch(file_path)
        
        # Save the sketch image
        sketch_path = os.path.join(UPLOAD_FOLDER, f"sketch_{file.filename}")
        sketch_img.save(sketch_path)
        
        # Return the sketch image
        return send_file(sketch_path, mimetype='image/png')

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Painting to Sketch Converter API!"})

if __name__ == '__main__':
    app.run(debug=True)



@app.route('/classify', methods=['POST'])
def classify_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        
        # Classify the image
        result = classify_image(file_path)
        
        return jsonify(result)
