import openai
import json

def get_key():
    with open("config.json", 'r') as fp:
        return json.load(fp)["secret-key"]

openai.api_key = get_key()

def make_caption(captions, class_label):

    suffix = "An important word to make the subject of your caption is {}.".format(class_label)
    # suffix = ""

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": "You are generating a caption for a single image for a model to generate a synthetic image. {}".format(suffix)},
            {"role": "user", "content": "I am going to provide you with several captions that were auto generated from many similar images." + \
            "Your job is to create a single caption that combines the most important and frequent elements of those captions along with the key word." + \
            "The captions might not include the key word, that is okay. It is your job to ensure it is in the final caption. Respond with only your new caption."},
            {"role": "user", "content": "Here are the captions, separated by newlines: {}".format('\n'.join(captions))}
        ]
    )

    new_caption = response['choices'][0]['message']['content']
    print(response)

    return new_caption

