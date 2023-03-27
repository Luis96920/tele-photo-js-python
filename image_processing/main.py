import os
import boto3
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from image_processing import process_image

app = Flask(__name__)

# Configure the S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id="YOUR_AWS_ACCESS_KEY",
    aws_secret_access_key="YOUR_AWS_SECRET_KEY",
    region_name="YOUR_AWS_REGION",
)

# Set up the S3 bucket and folder names
S3_BUCKET_NAME = "your-s3-bucket"
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
    filename = secure_filename(image.filename)

    # Upload the original image
    original_url = upload_file_to_s3(image, ORIGINAL_FOLDER, filename)

    # Process the image
    processed_image = process_image(image)  # Implement this function in the image_processing.py file

    # Upload the processed image
    processed_filename = f"{os.path.splitext(filename)[0]}-processed{os.path.splitext(filename)[1]}"
    processed_url = upload_file_to_s3(processed_image, PROCESSED_FOLDER, processed_filename)

    return jsonify(status="success", original_url=original_url, processed_url=processed_url)


if __name__ == "__main__":
    app.run(debug=True)
