import os
from flask import Flask, request, render_template, send_from_directory
from utils import *
app = Flask(__name__)



@app.route('/')
def index():
    # return "Welcome to the PDF Processing Web App. <a href='/upload'>Upload a PDF</a>"
    return render_template('upload.html')

# Create a route for uploading and processing PDFs


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
            input_pdf = os.path.join('uploads', uploaded_file.filename)

            uploaded_file.save(input_pdf)

            process_pdf(input_pdf, lower_color, upper_color)
            
            input_name = os.path.splitext(os.path.basename(input_pdf))[0]
            output_pdf_path = os.path.join('output', f'{input_name}_notes.pdf') 
            if os.path.exists(output_pdf_path): 
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
