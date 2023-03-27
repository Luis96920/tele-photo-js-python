import os
import boto3
from flask import Flask, request, jsonify
import uuid
import json
from image_processing import process_image
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins by default

def get_keys():
    with open("config.json", 'r') as fp:
        d = json.load(fp)
        return d

# Configure the S3 client
key_dict = get_keys()
s3 = boto3.client(
    "s3",
    aws_access_key_id=key_dict["aws-access-key"],
    aws_secret_access_key=key_dict["aws-secret-key"],
    region_name="us-east-2",
)

# Set up the S3 bucket and folder names
S3_BUCKET_NAME = "tele-photo"
ORIGINAL_FOLDER = "original-images/"
PROCESSED_FOLDER = "processed-images/"


import datetime

def upload_file_to_s3(file, folder, filename):
    s3.upload_fileobj(file, S3_BUCKET_NAME, folder + filename)
    
    # Generate a pre-signed URL
    file_url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": S3_BUCKET_NAME, "Key": folder + filename},
        ExpiresIn=datetime.timedelta(hours=1).total_seconds(),
    )

    return file_url



@app.route("/upload_and_process", methods=["POST"])
def upload_and_process():
    if "image" not in request.files:
        return jsonify(status="error", message="No image file provided."), 400

    image = request.files["image"]
    filename = str(uuid.uuid1()) + ".jpg"

    # Upload the original image
    original_url = upload_file_to_s3(image, ORIGINAL_FOLDER, filename)

    # Process the image
    processed_image = image # process_image(image)  # Implement this function in the image_processing.py file

    # Upload the processed image
    processed_filename = f"{os.path.splitext(filename)[0]}-processed{os.path.splitext(filename)[1]}"
    processed_url = upload_file_to_s3(processed_image, PROCESSED_FOLDER, processed_filename)

    response = jsonify(status="success", original_url=original_url, processed_url=processed_url)
        
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

    return response

# @app.after_request
# def after_request(response):
#   response.headers.add('Access-Control-Allow-Origin', '*')
#   response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#   response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#   return response

if __name__ == "__main__":
    app.run(debug=True)
