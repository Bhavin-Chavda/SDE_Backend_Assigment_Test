from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from config import Config
from datetime import datetime
import os
import pandas as pd
import requests
from PIL import Image

app = Flask(__name__)

# Load MySQL configurations from the Config class
app.config.from_object(Config)

# Initialize MySQL
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/createRequestID', methods=['POST'])
def create_request_id():
    file = request.files['file']
    if file and file.filename.endswith('.csv'):
        originalfilename = file.filename
        
        # Save the file
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename, file_extension = os.path.splitext(file.filename)
        new_filename = f"{filename}_{current_time}{file_extension}"
        
        file.save(os.path.join('files/', new_filename))
        print(new_filename)

        conn = mysql.connection
        cursor = conn.cursor()
        
        query = "INSERT INTO requestfilemapping (filename, newfilename) VALUES (%s, %s)"
        cursor.execute(query, (originalfilename, new_filename))
        
        conn.commit()
        
        generated_request_id = cursor.lastrowid
        print(f"Generated Request ID: {generated_request_id}")

        cursor.close()

        ProcessImagesRequestProductWise(new_filename , generated_request_id)

        return render_template('upload.html', message=f"Request ID Generated is: {generated_request_id}")
    else:
        return render_template('upload.html', message="Please upload a CSV file.")


def ProcessImagesRequestProductWise(new_filename , generated_request_id):

    print("New File name is : " + new_filename)

    df = pd.read_csv('files/'+new_filename)

    # Open Connection
    conn = mysql.connection
    cursor = conn.cursor()

    for _, row in df.iterrows():
        serial_number = row['Serial Number']
        product = row['Product']
        images = row['Images'].split(',')

        cnt = 1
        for image in images:
            
            save_directory = generate_save_directory(generated_request_id)
            LocalOriginalImagePath = generate_local_original_image_path(generated_request_id, product,cnt)
            # print(f"Full Local Path: images\{generated_request_id}\{LocalOriginalImagePath}")
            save_path = os.path.join(save_directory, LocalOriginalImagePath)
            os.makedirs(save_directory, exist_ok=True)
            cnt=cnt+1
            # print(" SavePath : "+save_path )
            print(type(save_path))

            # Download Image into local to process it
            LocalOriginalImagePathToSave = download_image(image,save_path)

            #Process the Image

            LocalProcessedImagePath = create_processed_image_and_save(save_path,generated_request_id,product,cnt)

            boolIsprocessed = 1
            if(LocalProcessedImagePath=="LocalProcessedImagePath"):
                boolIsprocessed = 1



            query = """
            INSERT INTO RequestProductImages (RequestID, ProductName, SerialNumber, ImageURL, 
            LocalOriginalImagePath, LocalProcessedImagePath, IsProcessed)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (generated_request_id, product, serial_number, image, LocalOriginalImagePathToSave, LocalProcessedImagePath, boolIsprocessed))


    conn.commit()
    cursor.close()


        
    return ""

def generate_save_directory(generated_request_id):
    return f"Images\OriginaImages\{generated_request_id}"

def generate_local_original_image_path(generated_request_id, product,cnt):
    return f"RequestID_{generated_request_id}_Product_{product}_Image{cnt}.jpg"

def download_image(url, save_path):
    
    try:
        # Send a GET request to the image URL
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for request errors

        # Open the file in binary write mode
        with open(save_path, 'wb') as file:
            # Write the content to the file
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        return save_path
        # print(f"Image successfully downloaded and saved to {save_path}")

    except requests.exceptions.RequestException as e:
        return f"Failed to download image. Error: {e}"


def create_processed_image_and_save(save_path,generated_request_id,product,cnt):
    
    output_directory = generate_save_processed_directory(generated_request_id)
    os.makedirs(output_directory, exist_ok=True)

    print(type(save_path))
    
    try:
        file_name, file_extension = os.path.splitext(os.path.basename(save_path))
        
        new_file_name = f"{file_name}_Processed{file_extension}"
        
        print(new_file_name)
        # Create the new save path
        new_save_path = os.path.join(output_directory, new_file_name)
        print(new_save_path)
        # Open the original image
        with Image.open(save_path) as img:
            if file_extension.lower() in ['.jpg', '.jpeg']:
                img.save(new_save_path, quality=50, optimize=True)
            else:
                # For other formats, use default saving options
                img.save(new_save_path)
            
        return new_save_path
        
    except Exception as e:
        # return f"Failed to process image. Error: {e}"
        return "ERROR OCCURED"

    return ""

def generate_save_processed_directory(generated_request_id):
    return f"Images\ProcessedImages\{generated_request_id}"

# def generate_local_processed_image_path(generated_request_id, product,cnt):
#     return f"RequestID_{generated_request_id}_Product_{product}_Image{cnt}.jpg"

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/requests')
def request_page():
    # Open Connection
    conn = mysql.connection
    cursor = conn.cursor()

    # Insert the filename into the database
    query = "SELECT request_id,newfilename,current_date_time FROM REQUESTFILEMAPPING ORDER BY current_date_time DESC"
    cursor.execute(query)
    all_requests = cursor.fetchall()
        
    all_requests = [{'request_id': row[0], 'newfilename': row[1],'current_date_time': row[2]} for row in all_requests]
    # Commit the transaction
    conn.commit()
    cursor.close()


    print("This is All Requests: ")
    print(all_requests)
    return render_template('request.html' , all_requests=all_requests)


@app.route('/requestDetailpage/<int:request_id>')
def request_page_detail(request_id):

    current_directory = os.path.dirname(os.path.abspath(__file__))

    conn = mysql.connection
    cursor = conn.cursor()

    query = "SELECT LocalOriginalImagePath, LocalProcessedImagePath FROM RequestProductImages WHERE RequestID = %s"
    cursor.execute(query, (request_id,))
    all_requests_images = cursor.fetchall()
        
    all_requests_images = [
        {
            'LocalOriginalImagePath': os.path.join(current_directory, row[0]),
            'LocalProcessedImagePath': os.path.join(current_directory, row[1])
        }
        for row in all_requests_images
    ]

    conn.commit()
    cursor.close()

    # return f"Request ID is found{request_id}"
    return render_template('requestDetail.html' , request_id=request_id , all_requests_images=all_requests_images)


if __name__ == '__main__':
    app.run(debug=True)
