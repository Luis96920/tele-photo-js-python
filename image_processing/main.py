import os, io, time
import boto3
from flask import Flask, request, jsonify
import uuid
import json
from image_processing import predict_step
from flask_cors import CORS
from image_gen import get_new_image
import base64
import requests
from PIL import Image
from reduce_many_captions import make_caption
import magic
import re

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
# ORIGINAL_FOLDER = "original-images/"
PROCESSED_FOLDER = "processed-images/"


import datetime

def upload_file_to_s3(file, folder, filename):
    s3.upload_fileobj(file, S3_BUCKET_NAME, folder + filename)
    
    # Generate a pre-signed URL
    file_url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": S3_BUCKET_NAME, "Key": folder + filename},
        ExpiresIn=int(datetime.timedelta(minutes=10).total_seconds())
    )

    return file_url


def is_valid_image(file):
    mime = magic.from_buffer(file.stream.read(), mime=True)
    file.stream.seek(0)  # Reset the file stream position
    return mime.startswith('image/')

def clean_description(description):
    return re.sub(r'[^a-zA-Z0-9\-!@#. ]', '', description)


def upload_and_process_multi_image(images, description):
    
    captions = []
    for image in images:
        file_content = image.read()
        im_buffer = io.BytesIO(file_content)
        captions.append(caption_image(im_buffer))

    print(description)

    prompt = make_caption(captions, description)

    processed_url = generate_and_save_image(prompt)

    return prompt, processed_url

@app.route("/api/upload_and_process", methods=["POST"])
def upload_and_process():

    prompt = ""
    processed_url = ""

    if "image" not in request.files and "images[]" in request.files:
        
        if "images[]" not in request.files:
            return jsonify(status="error", message="No images files provided."), 400

        images = request.files.getlist('images[]')

        for image in images:
            print(image)
            if not is_valid_image(image):
                return jsonify(status="error", message="Invalid image file provided."), 400

        if 'description' not in request.form:
            return jsonify({'error': 'No description provided'}), 400

        description = clean_description(request.form['description'])
        if len(description) > 256:
            return jsonify({'error': 'Description must be 256 characters or fewer'}), 400
        
        prompt, processed_url = upload_and_process_multi_image(images, description)


    else:

        if "image" not in request.files:
            return jsonify(status="error", message="No image file provided."), 400

        image = request.files["image"]

        if not is_valid_image(image):
            return jsonify(status="error", message="No image file provided."), 400

        file_content = image.read()
        im_buffer = io.BytesIO(file_content)

        prompt, processed_url = generate_next_image(im_buffer)
    
    response = jsonify(status="success", processed_url=processed_url, caption=prompt)
        
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')

    return response

def check_url(url):
    try:
        start_str = "https://tele-photo.s3.amazonaws.com/processed-images/"
        if url[0:len(start_str)] != start_str:
            return False
        
        filename_str = start_str + "bf7da412-cec6-11ed-b80b-060f2440ce9d"
        proc_str = "-processed.jpg?"
        if url[len(filename_str): len(filename_str) + len(proc_str)] != proc_str:
            return False
        
        if "." in url[len(filename_str) + len(proc_str):]:
            return False

        remainder = url[len(filename_str) + len(proc_str):]
        if "X-Amz-Algorithm" in remainder and "X-Amz-Credential" in remainder and "X-Amz-SignedHeaders" in remainder:
            return True
        
        return False
    except:
        return False

@app.route("/api/url_and_process", methods=["POST"])
def url_and_process():
    data = request.json
    url = data.get('url', '')
    if url == '':
        return jsonify({'error': 'url key is missing or empty'}), 400

    if not check_url(url):
        return jsonify({'error': 'url is invalid'}), 403

    # Download the image using the signed URL
    response = requests.get(url)

    im_buffer = 0
    if response.status_code == 200:
        # Store the downloaded image in an io.BytesIO object
        im_buffer = io.BytesIO(response.content)

    prompt, processed_url = generate_next_image(im_buffer)
    
    response = jsonify(status="success", processed_url=processed_url, caption=prompt)
        
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')

    return response

def generate_next_image(im_buffer):

    prompt = caption_image(im_buffer)
    processed_url = generate_and_save_image(prompt)
    return prompt, processed_url

def generate_and_save_image(prompt):
    start = time.time()
    processed_image = get_new_image(prompt) # process_image(image)  # Implement this function in the image_processing.py file
    print("Image time: {}".format(round(time.time() - start, 2)))

    # Upload the processed image
    base_name = str(uuid.uuid1())
    processed_filename = "{}-processed.jpg".format(base_name)
    
    with open(processed_image, 'rb') as proc_im:
        processed_url = upload_file_to_s3(proc_im, PROCESSED_FOLDER, processed_filename)
    return processed_url

def caption_image(im_buffer):
    im_buffer_dup = io.BytesIO(im_buffer.read())
    im_buffer.seek(0)
    image_pil = Image.open(im_buffer_dup)

    # Process the image
    start = time.time()
    prompt = predict_step(image_pil)[0]
    print("Caption time: {}".format(round(time.time() - start, 2)))
    return prompt


if __name__ == "__main__":
    app.run(debug=True)
