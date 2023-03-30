import json
import os
import openai
import base64

def get_key():
    with open("config.json", 'r') as fp:
        return json.load(fp)["secret-key"]

openai.api_key = get_key()

def get_new_image(prompt):
    
    resp = openai.Image.create(
    prompt=prompt,
    n=1,
    size="256x256",
    response_format = "b64_json"
    )

    img_data = resp["data"][0]["b64_json"]

    with open("imageToSave.png", "wb") as fh:
        fh.write(base64.b64decode(img_data))

    return "imageToSave.png"

def main():
    get_new_image("cute doggy")

if __name__ == "__main__":
    main()