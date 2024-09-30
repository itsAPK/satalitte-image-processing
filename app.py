from flask import jsonify, request
from flask import Flask, render_template, request, redirect, url_for, send_file
import cv2
import numpy as np
import os
import pandas as pd
from werkzeug.utils import secure_filename
from openpyxl import Workbook

app = Flask(__name__)

# Set directories for image uploads and outputs
UPLOAD_FOLDER = 'uploads/'
OUTPUT_FOLDER = 'output/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Allowed extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Function to check if uploaded file has allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for the main page
@app.route('/')
def home():
    return render_template('index.html')


# Route to receive ROI coordinates and send back processed data
@app.route('/get_roi_data', methods=['POST'])
def get_roi_data():
    roi_coords = request.json
    startX = roi_coords['startX']
    startY = roi_coords['startY']
    endX = roi_coords['endX']
    endY = roi_coords['endY']

    # Calculate latitude, longitude, side lengths, and area based on ROI (this is placeholder logic)
    lat_long = [(40.7128, -74.0060), (40.7138, -74.0065), (40.7140, -74.0055), (40.7130, -74.0050)]
    side_lengths = [abs(endX - startX), abs(endY - startY)]
    area = side_lengths[0] * side_lengths[1]

    # Return the data as JSON
    return jsonify({
        'lat_long': lat_long,
        'side_lengths': side_lengths,
        'area': area
    })


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Perform image segmentation and ROI selection
        processed_image, roi_data = process_image(filepath)

        if processed_image is None or roi_data is None:
            return "Error processing image", 400  # Return an error response

        # Save the processed image
        output_filename = 'stencil_' + filename
        output_filepath = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        cv2.imwrite(output_filepath, processed_image)

        # Return the processed image and ROI data
        return render_template('index.html', filename=filename, processed_image=output_filename, roi_data=roi_data)

    return redirect(request.url)
# Route to export ROI data to Excel
@app.route('/export', methods=['POST'])
def export_to_excel():
    roi_data = request.form.get('roi_data')
    data = eval(roi_data)

    # Create an Excel file and write ROI data
    wb = Workbook()
    ws = wb.active
    ws.append(["Latitude 1", "Longitude 1", "Latitude 2", "Longitude 2", "Side Lengths", "Area"])
    ws.append(data)

    output_filepath = os.path.join(app.config['OUTPUT_FOLDER'], 'roi_data.xlsx')
    wb.save(output_filepath)

    return send_file(output_filepath, as_attachment=True)

def process_image(filepath):
    # Load the image
    image = cv2.imread(filepath)

    if image is None:
        print("Error: Image could not be loaded.")
        return None, None  # Return None if image loading fails

    # Perform semantic segmentation (placeholder)
    stencil_image = np.zeros_like(image)
    stencil_image[image[:, :, 0] > 100] = [255, 0, 0]  # Example segmentation logic

    # ROI (manually chosen here as an example)
    roi_coords = [(50, 50), (200, 50), (200, 200), (50, 200)]  # Example coordinates
    cv2.polylines(stencil_image, [np.array(roi_coords)], True, (0, 255, 0), 2)

    # Placeholder logic for lat/long
    lat_long = [(40.7128, -74.0060), (40.7138, -74.0065), (40.7140, -74.0055), (40.7130, -74.0050)]
    side_lengths = [150, 150]  # Example values
    area = side_lengths[0] * side_lengths[1]  # Example value for rectangular area

    # Collect data to return
    roi_data = {
        'lat_long': lat_long,
        'side_lengths': side_lengths,
        'area': area
    }

    return stencil_image, roi_data  # Return both processed image and ROI data
 
if __name__ == "__main__":
    app.run(debug=True)