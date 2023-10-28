import os
import cv2
import numpy as np
import fitz
from PIL import Image
import img2pdf
import argparse
from tqdm.auto import tqdm
import shutil
from flask import Flask, request, render_template, send_file, send_from_directory, url_for
from utils import *
app = Flask(__name__)



@app.route('/')
def index():
    # return "Welcome to the PDF Processing Web App. <a href='/upload'>Upload a PDF</a>"
    return render_template('upload.html')

# Create a route for uploading and processing PDFs

def pdf_processor(input_pdf_path, lower_color, upper_color):
    output_pdf = process_pdf(input_pdf_path, lower_color, upper_color)
    return output_pdf

@app.route('/upload', methods=['GET', 'POST'])
def upload_pdf():
    sys_clean()

    download_link = None
    color_choice = 'yellow'  # Default color choice
    lower_color, upper_color = (82, 225, 245), (150, 250, 255)  # Default values for yellow

    if request.method == 'POST':
        uploaded_file = request.files['file']
        color_choice = request.form.get('color_choice')  # Get the user's color choice

        if color_choice == 'green':
            lower_color, upper_color = (0, 165, 0), (215, 255, 168)  # Use green color values

        if uploaded_file.filename != '':
            input_pdf_path = os.path.join('uploads', uploaded_file.filename)
            uploaded_file.save(input_pdf_path)
            output_pdf_path = pdf_processor(input_pdf_path, lower_color, upper_color)  # Process the uploaded PDF with the selected color
            download_link = '/download/' + os.path.basename(output_pdf_path)

    return render_template('upload.html', download_link=download_link, color_choice=color_choice)


@app.route('/download/<path:pdf_filename>')
def download_pdf(pdf_filename):
    # Specify the directory where the processed PDFs are stored
    output_dir = 'output'
    try:
        return send_from_directory(output_dir, pdf_filename, as_attachment=True)
    except Exception as e:
        return str(e)  # Print any error that occurs during file retrieval


if __name__ == "__main__":
    app.run()
