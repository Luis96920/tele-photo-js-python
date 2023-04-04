import os
import random
from image_gen import get_new_image
from reduce_many_captions import make_caption
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
from PIL import Image

model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

max_length = 16
num_beams = 4
gen_kwargs = {"max_length": max_length, "num_beams": num_beams}
def predict_images_from_paths(paths):
    image_captions = [predict_step(Image.open(p))[0] for p in paths]
    return image_captions

def predict_step(pil_image):
  images = [remove_alpha_channel(pil_image)]

  pixel_values = feature_extractor(images=images, return_tensors="pt").pixel_values
  pixel_values = pixel_values.to(device)

  output_ids = model.generate(pixel_values, **gen_kwargs)

  preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
  preds = [pred.strip() for pred in preds]
  return preds

def remove_alpha_channel(image):
    if image.mode == 'RGBA':
        # Create a new RGB image with a white background
        rgb_image = Image.new('RGB', image.size, (255, 255, 255))
        
        # Paste the original image onto the white background, ignoring the alpha channel
        rgb_image.paste(image, mask=image.split()[3])  # The alpha channel is the fourth band (index 3)
        
        return rgb_image
    else:
        # If the image does not have an alpha channel, return it unchanged
        return image

def list_files(path):
    files = [os.path.join(path, file) for file in os.listdir(path)]

    # Calculate the number of files to sample
    n_percent = 1  # set the percentage to sample
    n_files = int(len(files) * n_percent / 100)

    # Select a random sample of files
    random_files = random.sample(files, n_files)
    return random_files

if __name__ == "__main__":
    # test_image = 'imageToSave.png'
    # test_image = "/home/ben/Data/classic_benchmarks/ImageNetSample_3/Koala/n01882714_7.JPEG"
    # print(predict_images_from_paths([test_image])) 

    path = "/home/ben/Data/classic_benchmarks/ImageNetSample_3/SeaTurtle"
    paths = list_files(path)

    caption_list = predict_images_from_paths(paths)

    new_caption = make_caption(caption_list, path.split("/")[-1])

    print(new_caption)

    get_new_image(new_caption)

