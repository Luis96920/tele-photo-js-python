import json
import os
import openai

def get_key():
    with open("config.json", 'r') as fp:
        return json.load(fp)["secret-key"]
openai.api_key = get_key()

def get_new_image():
    
    resp = openai.Image.create(
    prompt="A cute baby sea otter",
    n=1,
    size="512x512"
    )

    print(resp["data"])

def main():
    get_new_image()

if __name__ == "__main__":
    main()