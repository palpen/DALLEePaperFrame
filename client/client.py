import io
import random
import time

import requests
import inky
import argparse
from PIL import Image

from frame_composer import FrameComposer
from buttons import set_button_function, wait_forever_for_button_presses

display = inky.auto()
width, height = display.resolution

fc = FrameComposer(width, height)

last_creation_time = 0
minimum_time_between_image_generations = 5

with open("prompts.txt") as file:
    prompts = file.readlines()
    prompts = [p.rstrip() for p in prompts]

pre_prompts = ['',
               '',
               'a cartoon of',
               'a painting of',
               'a drawing of']


def generate_sample_prompt():
    """
    Generates a random prompt from the list of prompts and a random pre-prompt.
    :return: a string containing the prompt
    """
    pp = random.choice(pre_prompts)
    p = random.choice(prompts)
    return pp + ' ' + p if pp != '' else p


def generate_new_image(text_prompt, generated_image_size=350):
    print('Generating new image...')

    # request the image from the server
    response = requests.get('http://' + args.server_address + ':' + args.server_port +
                            '/generate/' + text_prompt + '?size={}'.format(generated_image_size))
    generated_image = Image.open(io.BytesIO(response.content))

    print("Received image from server")
    return generated_image


def display_image_on_frame(image, text_prompt):
    print("Displaying image on frame")
    frame_image = fc.create_frame_image(image, text_prompt)
    display.set_image(frame_image)
    display.set_border(inky.BLACK)
    display.show()
    print("Displayed image on display")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server-address', help='Server address')
    parser.add_argument('-p', '--server-port', default='8000', help='Server port')

    args = parser.parse_args()

    GENERATOR_TEXT_PROMPT = generate_sample_prompt()


    def display_new_generated_image_w_same_prompt(_):
        global last_creation_time

        if time.time() - last_creation_time > minimum_time_between_image_generations:  # debounce the button press
            global GENERATOR_TEXT_PROMPT

            # generate and display a new image
            generated_image = generate_new_image(GENERATOR_TEXT_PROMPT)
            display_image_on_frame(generated_image, GENERATOR_TEXT_PROMPT)

            last_creation_time = time.time()


    def display_new_generated_image_w_new_prompt(_):
        global last_creation_time

        if time.time() - last_creation_time > minimum_time_between_image_generations:  # debounce the button press
            global GENERATOR_TEXT_PROMPT

            GENERATOR_TEXT_PROMPT = generate_sample_prompt()  # generate a new prompt

            # generate and display a new image
            generated_image = generate_new_image(GENERATOR_TEXT_PROMPT)
            display_image_on_frame(generated_image, GENERATOR_TEXT_PROMPT)

            last_creation_time = time.time()


    # Set up the buttons
    set_button_function('A', display_new_generated_image_w_same_prompt)
    set_button_function('B', display_new_generated_image_w_new_prompt)
    set_button_function('C', lambda _: print('C pressed'))
    set_button_function('D', lambda _: print('D pressed'))

    # Wait forever for button presses (ie while true)
    print("Setup complete. Waiting for button presses...")
    wait_forever_for_button_presses()
