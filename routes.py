import os
from flask import render_template, request, send_file, current_app
import requests
from PIL import Image
import tempfile
import shutil

from app import app

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_page = int(request.form['start_page'])
        end_page = int(request.form['end_page'])
        url = request.form['url']
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, 'output.pdf')
        
        try:
            # Your existing functions modified for web use
            def get_url(link_sach):
                a = link_sach.replace("FullBookReader.aspx?Url=/pages/cms/", "")
                return a[:-49]

            return_url = get_url(url)
            
            # Download images to temp directory
            img_dir = os.path.join(temp_dir, 'imgs')
            os.makedirs(img_dir)
            
            for i in range(start_page, end_page + 1):
                generated_url = (return_url + f'FullPreview/{str(i).zfill(6)}.jpg')
                response = requests.get(generated_url)
                if response.status_code == 200:
                    with open(os.path.join(img_dir, f'{str(i).zfill(6)}.jpg'), 'wb') as handle:
                        handle.write(response.content)

            # Convert to PDF
            img_list = []
            for i in range(start_page, end_page + 1):
                with Image.open(os.path.join(img_dir, f'{str(i).zfill(6)}.jpg')) as image:
                    img_list.append(image.convert('RGB'))

            img_list[0].save(pdf_path, save_all=True, append_images=img_list[1:])
            
            # Send file to user
            return send_file(pdf_path, as_attachment=True, download_name='document.pdf')
            
        finally:
            # Clean up temp directory
            shutil.rmtree(temp_dir)
            
    return render_template('index.html')
