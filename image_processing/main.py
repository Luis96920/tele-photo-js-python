import os, io
import boto3
from flask import Flask, request, jsonify
import uuid
import json
from image_processing import predict_step
from flask_cors import CORS
from image_gen import get_new_image
import base64
from PIL import Image
import magic

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
        ExpiresIn=int(datetime.timedelta(hours=1).total_seconds())
    )

    return file_url


def is_valid_image(file):
    mime = magic.from_buffer(file.stream.read(), mime=True)
    file.stream.seek(0)  # Reset the file stream position
    return mime.startswith('image/')


@app.route("/api/upload_and_process", methods=["POST"])
def upload_and_process():
    if "image" not in request.files:
        return jsonify(status="error", message="No image file provided."), 400

    print("Req: {}".format(request))

    image = request.files["image"]
    rounds = request.files["number"]


    if not is_valid_image(image):
        return jsonify(status="error", message="No image file provided."), 400

    file_content = image.read()

    im_buffer = io.BytesIO(file_content)
    im_buffer_dup = io.BytesIO(im_buffer.read())
    im_buffer.seek(0)
    image_pil = Image.open(im_buffer_dup)

    base_name = str(uuid.uuid1())
    filename = base_name + ".jpg"

    # Upload the original image
    original_url = upload_file_to_s3(im_buffer, ORIGINAL_FOLDER, filename)

    # Process the image
    prompt = predict_step(image_pil)[0]
    processed_image = get_new_image(prompt) # process_image(image)  # Implement this function in the image_processing.py file

    # Upload the processed image
    processed_filename = "{}-processed.jpg".format(base_name)
    with open(processed_image, 'rb') as proc_im:
        processed_url = upload_file_to_s3(proc_im, PROCESSED_FOLDER, processed_filename)

    resp_list = []
    for i in range(rounds):
        resp_list.append({
            'original_url': original_url,
            'processed_url': processed_url,
            'caption': prompt
        })

    response = jsonify(status="success", data=resp_list)
        
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
