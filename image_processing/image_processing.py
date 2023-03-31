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
def predict_step(pil_image):
  images = [remove_alpha_channel(pil_image)]

  pixel_values = feature_extractor(images=images, return_tensors="pt").pixel_values
  pixel_values = pixel_values.to(device)

  output_ids = model.generate(pixel_values, **gen_kwargs)

  preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
  preds = [pred.strip() for pred in preds]
  return preds

from PIL import Image

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


if __name__ == "__main__":
    print(predict_step(['imageToSave.png'])) 


