import argparse
import datetime
import io
import json
import os.path
import random
import sys
import time
import threading

import requests
import inky
import yaml
import tweepy
from PIL import Image

import tweets_utils
from frame_composer import FrameComposer
from buttons import set_button_function, wait_forever_for_button_presses
from record_audio import record_audio


GENERATED_IMAGE_SIZE = 400  # Image size to pass to API (image returned is a square)
MINIMUM_TIME_BETWEEN_IMAGE_GENERATIONS = 5

MAX_NUM_IMAGES_TO_DISPLAY = 5  # If more than 5 images are generated within TIME_THRESHOLD, kill the program
TIME_THRESHOLD = 180  # We cannot display more than MAX_NUM_IMAGES_TO_DISPLAY in less than MAX_TIME

AUTOMATED_IMAGE_GENERATION = True
AUTOMATED_IMAGE_GENERATION_TIME = 60 * 60 * 1  # 1 hours

TIME_INTERVAL_CHECK_TWITTER = 5  # How frequently should the client check Twitter for new text prompts (seconds)

SAVED_IMAGE_FOLDER = 'saved_images'


# State variables
last_creation_time = 0
num_images_displayed = 0
last_display_time = 0
generator_text_prompt = "a cat"

# Get parent directory of this file
abs_path = os.path.dirname(os.path.abspath(__file__))


# Load configuration variables
with open(f"{os.path.dirname(abs_path)}/twitter_api_keys.yml", "r") as stream:
    try:
        twitter_api_keys = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
	    print(exc)

with open(f"{os.path.dirname(abs_path)}/prompts_config.yml", "r") as stream:
    try:
        prompts_config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
pre_prompts = prompts_config["pre_prompts"]
prompts = prompts_config["prompts"]


# Initialize display
display = inky.auto()
width, height = display.resolution
print(f"Display width and height: {width}, {height}")
fc = FrameComposer(width, height)


# Initialize folder to store images generated in
# TODO: If SAVED_IMAGE_FOLDER is empty, generate some image and save it,
# perhaps a message to turn on the server
if not os.path.exists(SAVED_IMAGE_FOLDER):
    os.makedirs(SAVED_IMAGE_FOLDER)


# Setup Twitter API access
# Twitter API v2
client = tweepy.Client(
	bearer_token=twitter_api_keys["bearer_token"],
	consumer_key=twitter_api_keys["consumer_key"],
	consumer_secret=twitter_api_keys["consumer_secret"],
	access_token=twitter_api_keys["access_token_key"],
	access_token_secret=twitter_api_keys["access_token_secret"]
)
# Twitter API v1 (needed for uploading media as a tweet)
auth = tweepy.OAuthHandler(twitter_api_keys["consumer_key"], twitter_api_keys["consumer_secret"])
auth.set_access_token(twitter_api_keys["access_token_key"], twitter_api_keys["access_token_secret"])
api = tweepy.API(auth)


def generate_sample_prompt():
    """
    Generates a random prompt from the list of prompts and a random pre-prompt.
    :return: a string containing the prompt
    """
    pp = random.choice(pre_prompts)
    p = random.choice(prompts)
    return pp + ' ' + p if pp != '' else p


def generate_new_image(text_prompt, generated_image_size=GENERATED_IMAGE_SIZE):
    print('Generating new image...')

    # request the image from the server
    response = requests.get('http://' + args.server_address + ':' + args.server_port +
                            '/generate/' + text_prompt + '?size={}'.format(generated_image_size))
    generated_image = Image.open(io.BytesIO(response.content))

    print("Received image from server")
    return generated_image


def display_image_on_frame(image, text_prompt):
    """Display image and text prompt on ePaper frame

    To protect the frame from bugs that might cause it to refresh with new images
    repeatedly, we restrict the number of images that can be displaed over
    a span of time. Specifically, no more than MAX_NUM_IMAGES_TO_DISPLAY display
    refreshes are allowed over a span of time set in TIME_THRESHOLD.
    """
    global num_images_displayed, last_display_time

    if num_images_displayed > MAX_NUM_IMAGES_TO_DISPLAY:
        print(
            f"You displayed more than the allowable amount in the time interval of {TIME_THRESHOLD}."
            "This will stop the program to protect the ePaper frame. Good bye."
        )
        sys.exit(1)

    if time.time() - last_display_time < TIME_THRESHOLD:
        num_images_displayed += 1
        print(f"Incremented display counter. Current count: {num_images_displayed}")
    else:
        num_images_displayed = 0

    frame_image = fc.create_frame_image(image, text_prompt)
    display.set_image(frame_image)
    display.set_border(inky.BLACK)
    display.show()

    last_display_time = time.time()

    print(f"Displayed image on display at {datetime.datetime.now()}")


def save_image_to_file(image, text_prompt):
    full_path = os.path.join(SAVED_IMAGE_FOLDER, text_prompt.replace(' ', '_') + '.png')
    image.save(full_path)
    print(f"File saved to {full_path}")

    # remove the oldest image if there are more than 100 images in the folder
    image_files = os.listdir(SAVED_IMAGE_FOLDER)
    if len(image_files) > 100:
        files = [os.path.join(SAVED_IMAGE_FOLDER, f) for f in image_files]
        oldest_file = sorted(files, key=os.path.getmtime)[0]
        print(f"Deleting {oldest_file}")
        os.remove(oldest_file)


def load_random_previously_generated_image():
    random_file_name = random.choice(os.listdir(SAVED_IMAGE_FOLDER))
    text_prompt = random_file_name.split('.')[0].replace('_', ' ')
    print(f"Loading a (randomly chosen) previously generated image from the text prompt \"{text_prompt}\"")
    return (
        Image.open(os.path.join(SAVED_IMAGE_FOLDER, random_file_name)),
        text_prompt
    )


#def get_text_prompt_from_audio(audio_file_name):
#    url = 'http://' + args.server_address + ':' + args.server_port + '/transcribe'
#    files = {'file': (audio_file_name, open(audio_file_name, 'rb'), 'audio/x-wav')}
#    response = requests.post(url, files=files)
#    text_prompt = response.text.replace('"', '').strip()
#    print("Received text prompt from server - {}".format(text_prompt))
#    return text_prompt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server-address', help='Server address')
    parser.add_argument('-p', '--server-port', default='8000', help='Server port')

    args = parser.parse_args()

    generator_text_prompt = generate_sample_prompt()


    def display_new_generated_image_from_tweet(_=None):
        global last_creation_time, generator_text_prompt
        print("Pressed display_new_generated_image_from_tweet button")

        # get text prompt from tweet
        tweet_id, generator_text_prompt = tweets_utils.retrieve_most_recent_text_prompt(client=client, configs=twitter_api_keys)

        if not generator_text_prompt:
            print(f"There are no recent tweets containing {tweets_utils.TEXT_PROMPT_HASHTAG}")
            generated_image, generator_text_prompt = load_random_previously_generated_image()
            display_image_on_frame(generated_image, generator_text_prompt)
            last_creation_time = time.time()
            # generator_text_prompt is now an empty string, seed it with a new prompt
            generator_text_prompt = generate_sample_prompt()
        elif server_is_on():
            if time.time() - last_creation_time > MINIMUM_TIME_BETWEEN_IMAGE_GENERATIONS:  # debounce the button press
                print(f"Text prompt from new tweet with id {tweet_id}: {generator_text_prompt}")
                # generate and display a new image
                try:
                    print("Generating image from tweet")
                    generated_image = generate_new_image(generator_text_prompt)
                    save_image_to_file(generated_image, generator_text_prompt)

                    # upload image as a reply to original text prompt tweet
                    print("Uploading image to Twitter")
                    api.update_status_with_media(
                        "",
                        filename=os.path.join(
                            SAVED_IMAGE_FOLDER,
                            generator_text_prompt.replace(' ', '_') + '.png'),
                        in_reply_to_status_id=tweet_id
                    )
                except Exception as e:
                    print("A problem occurred: ", e)
                    generated_image, generator_text_prompt = load_random_previously_generated_image()
                display_image_on_frame(generated_image, generator_text_prompt)
                last_creation_time = time.time()
        else:
            generated_image, generator_text_prompt = load_random_previously_generated_image()
            display_image_on_frame(generated_image, generator_text_prompt)
            last_creation_time = time.time()


    def display_new_generated_image_w_same_prompt(_=None):
        global last_creation_time, generator_text_prompt
        print("Pressed display_new_generated_image_w_same_prompt button")

        if server_is_on():
            if time.time() - last_creation_time > MINIMUM_TIME_BETWEEN_IMAGE_GENERATIONS:  # debounce the button press

                # generate and display a new image
                try:
                    generated_image = generate_new_image(generator_text_prompt)
                    save_image_to_file(generated_image, generator_text_prompt)

                    print("Uploading image to Twitter")
                    api.update_status_with_media(
                        generator_text_prompt + " #autogenerated",
                        filename=os.path.join(
                            SAVED_IMAGE_FOLDER,
                            generator_text_prompt.replace(' ', '_') + '.png'),
                    )
                except Exception as e:
                    print("A problem occurred at display_new_generated_image_w_same_prompt: ", e)
                    generated_image, generator_text_prompt = load_random_previously_generated_image()
                display_image_on_frame(generated_image, generator_text_prompt)
                last_creation_time = time.time()
        else:
            generated_image, generator_text_prompt = load_random_previously_generated_image()
            display_image_on_frame(generated_image, generator_text_prompt)
            last_creation_time = time.time()


    def display_new_generated_image_w_new_prompt(_=None):
        global last_creation_time, generator_text_prompt
        print("Pressed display_new_generated_image_w_new_prompt button")
        if server_is_on():
            if time.time() - last_creation_time > MINIMUM_TIME_BETWEEN_IMAGE_GENERATIONS:  # debounce the button press
                generator_text_prompt = generate_sample_prompt()  # generate a new prompt
                # generate and display a new image
                try:
                    generated_image = generate_new_image(generator_text_prompt)
                    save_image_to_file(generated_image, generator_text_prompt)

                    print("Uploading image to Twitter")
                    api.update_status_with_media(
                        generator_text_prompt + " #autogenerated",
                        filename=os.path.join(
                            SAVED_IMAGE_FOLDER,
                            generator_text_prompt.replace(' ', '_') + '.png'),
                    )
                except Exception as e:
                    print("A problem occurred at display_new_generated_image_w_new_prompt: ", e)
                    generated_image, generator_text_prompt = load_random_previously_generated_image()
                display_image_on_frame(generated_image, generator_text_prompt)
                last_creation_time = time.time()
        else:
            generated_image, generator_text_prompt = load_random_previously_generated_image()
            display_image_on_frame(generated_image, generator_text_prompt)
            last_creation_time = time.time()


    #def display_new_generated_image_w_recorded_prompt(_=None):
    #    global last_creation_time

    #    if time.time() - last_creation_time > MINIMUM_TIME_BETWEEN_IMAGE_GENERATIONS:
    #        global generator_text_prompt

    #        # record the user's voice
    #        print('Recording audio...')
    #        audio_file_name = record_audio()
    #        print('Finished recording audio')

    #        # get the text prompt from the audio file
    #        generator_text_prompt = get_text_prompt_from_audio(audio_file_name)

    #        # generate and display a new image
    #        try:
    #            generated_image = generate_new_image(generator_text_prompt)
    #            save_image_to_file(generated_image, generator_text_prompt)
    #        except Exception as e:
    #            print("A problem occurred: ", e)
    #            generated_image, generator_text_prompt = load_random_previously_generated_image()
    #        display_image_on_frame(generated_image, generator_text_prompt)

    #        last_creation_time = time.time()


    def server_is_on():
        try:
            response = requests.get(
                f"http://{args.server_address}:{args.server_port}/api_status",
                timeout=5
            )
            status = json.loads(response.content)
            if not all(
                [
                    status["is_server_live"],
                    status["is_server_ready"],
                    status["is_model_ready"],
                ]
            ):
                print(
                    "Something is not working...\n"
                    f"is_server_live: {status['is_server_live']}\n"
                    f"is_server_ready: {status['is_server_ready']}\n"
                    f"is_model_ready: {status['is_model_ready']}"
                )
                return False
            return True
        except Exception as e:
            print(f"Failed to get a response from the server: {e}")
            return False


    def toggle_auto_image_generation(_=None):
        global AUTOMATED_IMAGE_GENERATION
        AUTOMATED_IMAGE_GENERATION = not AUTOMATED_IMAGE_GENERATION

        if AUTOMATED_IMAGE_GENERATION:
            print("Automated image generation enabled")
        else:
            print("Automated image generation disabled")


    # Set up the buttons
    set_button_function('A', display_new_generated_image_from_tweet)
    set_button_function('B', display_new_generated_image_w_new_prompt)
    set_button_function('C', display_new_generated_image_w_same_prompt)
    #set_button_function('C', display_new_generated_image_w_recorded_prompt)
    set_button_function('D', toggle_auto_image_generation)


    def image_generation_timer():
        """Set display to auto create a new image every N hours
        """
        global last_creation_time
        if server_is_on():
            if AUTOMATED_IMAGE_GENERATION and time.time() - last_creation_time > MINIMUM_TIME_BETWEEN_IMAGE_GENERATIONS:
                print('Automated image generation started')
                random.choice([display_new_generated_image_w_same_prompt, display_new_generated_image_w_new_prompt])()
            threading.Timer(AUTOMATED_IMAGE_GENERATION_TIME, image_generation_timer).start()
        else:
            generated_image, generator_text_prompt = load_random_previously_generated_image()
            display_image_on_frame(generated_image, generator_text_prompt)
            last_creation_time = time.time()
            threading.Timer(AUTOMATED_IMAGE_GENERATION_TIME, image_generation_timer).start()


    def check_recent_tweets_and_generate_image_if_new():
        """Checks if the most recent tweet is a text prompt and if an image
        is yet to be generated for it. If both previous statements are true,
        then generate an image for it.
        """
        _, text_prompt = tweets_utils.retrieve_most_recent_text_prompt(
            client=client, configs=twitter_api_keys
        )
        image_filename = os.path.join(
            SAVED_IMAGE_FOLDER,
            text_prompt.replace(' ', '_') + '.png'
        )
        if not text_prompt:
            # The last MAX_NUM_TWEETS_TO_RETRIVE number of tweets does not include
            # the trigger hashtag TEXT_PROMPT_HASHTAG so continue monitoring Twitter
            threading.Timer(
                TIME_INTERVAL_CHECK_TWITTER,
                check_recent_tweets_and_generate_image_if_new
            ).start()
        elif (
                server_is_on()
                and not os.path.isfile(image_filename)
                and time.time() - last_creation_time > MINIMUM_TIME_BETWEEN_IMAGE_GENERATIONS
        ):
            print("Generating image from a new tweet!")
            display_new_generated_image_from_tweet()
            threading.Timer(
                TIME_INTERVAL_CHECK_TWITTER,
                check_recent_tweets_and_generate_image_if_new
            ).start()
        else:
            threading.Timer(
                TIME_INTERVAL_CHECK_TWITTER,
                check_recent_tweets_and_generate_image_if_new
            ).start()


    image_generation_timer()
    check_recent_tweets_and_generate_image_if_new()


    # Wait forever for button presses (ie while true)
    print("Setup complete. Waiting for button presses...")
    wait_forever_for_button_presses()
