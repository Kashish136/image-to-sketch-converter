import numpy as np
import imageio
import scipy.ndimage
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os

# Initialize Flask app
app = Flask(__name__)
UPLOAD_FOLDER = 'user_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to convert RGB image to grayscale
def grayscale_img(rgb):
    return np.dot(rgb[..., :3], [0.299, 0.587, 0.114])

# Function to apply the dodging effect
def dodge(blur_img, gray_img):
    result = blur_img * 255 / (255 - gray_img)
    result[result > 255] = 255
    result[gray_img == 255] = 255
    return result.astype("uint8")

# Main function to convert an image to a sketch
def convert_to_sketch(image_path, blur_sigma=5):
    try:
        # Load the image
        source_img = imageio.imread(image_path)

        # Convert to grayscale
        grayscale_image = grayscale_img(source_img)

        # Invert the grayscale image
        inverted_image = 255 - grayscale_image

        # Blur the inverted image using Gaussian filter
        blurred_image = scipy.ndimage.gaussian_filter(inverted_image, sigma=blur_sigma)

        # Generate the sketch using dodging
        sketch_image = dodge(blurred_image, grayscale_image)

        return sketch_image
    except Exception as e:
        raise ValueError(f"Error processing the image: {e}")

# Flask route for uploading and processing images
@app.route('/upload', methods=['POST'])
def upload_and_process_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded file securely
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        # Convert the image to a sketch
        sketch_image = convert_to_sketch(file_path)

        # Save the sketch to a file
        sketch_path = os.path.join(app.config['UPLOAD_FOLDER'], f"sketch_{filename}")
        plt.imsave(sketch_path, sketch_image, cmap="gray", vmin=0, vmax=255)

        # Return the sketch file
        return send_file(sketch_path, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": f"Failed to process the image: {e}"}), 500

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Sketch Converter API! Use the '/upload' endpoint to upload an image."})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
