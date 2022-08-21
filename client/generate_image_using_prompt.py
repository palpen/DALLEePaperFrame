"""
Usage:
    python generate_image_using_prompt -tp "A painting of a cat"
"""

import argparse
import io
import json

import requests
from PIL import Image, ImageDraw


GENERATED_IMAGE_SIZE = 400
SERVER_IP_ADDRESS = "10.0.0.87"
PORT = "8000"

parser = argparse.ArgumentParser()
parser.add_argument('-tp', '--text-prompt', help='Text prompt')
args = parser.parse_args()

############################
# Check status of endpoint #
############################
response = requests.get(f'http://{SERVER_IP_ADDRESS}:{PORT}/api_status', timeout=3)
print(response.ok, response.status_code, response.content)
print(json.loads(response.content))

######################
# Generate new image #
######################
print('Generating new image...')
response = requests.get(f'http://{SERVER_IP_ADDRESS}:{PORT}/generate/{args.text_prompt}?size={GENERATED_IMAGE_SIZE}')
generated_image = Image.open(io.BytesIO(response.content))
print(type(generated_image))
print("Received image from server")

# UNCOMMENT TO DISPLAY IMAGE ON FRAME
#from client import display_image_on_frame
#display_image_on_frame(generated_image, args.text_prompt)
