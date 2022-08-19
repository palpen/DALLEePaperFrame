"""
Usage:
    python generate_image_using_prompt -tp "A painting of a cat"
"""

import argparse
import io

import requests
import inky
from PIL import Image, ImageDraw

from client import display_image_on_frame


GENERATED_IMAGE_SIZE = 350
SERVER_IP_ADDRESS = "10.0.0.87"
PORT = "8000"

parser = argparse.ArgumentParser()
parser.add_argument('-tp', '--text-prompt', help='Text prompt')
args = parser.parse_args()

print('Generating new image...')
response = requests.get(f'http://{SERVER_IP_ADDRESS}:{PORT}/generate/{args.text_prompt}?size={GENERATED_IMAGE_SIZE}')
generated_image = Image.open(io.BytesIO(response.content))
print("Received image from server")
display_image_on_frame(generated_image, args.text_prompt)
