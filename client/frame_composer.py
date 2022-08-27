from PIL import Image, ImageDraw, ImageFont


# MAX_CHARACTERS is the max number of characters that single line can have.
# If the text prompt exceeds this value, then split the text prompt into two
# lines with the first line having at most MAX_WORDS number of words.
MAX_CHARACTERS = 40
MAX_WORDS = 9


class FrameComposer:
    def __init__(self, width, height):

        # Display dimensions
        self.width = width
        self.height = height

        # Text prompt properties
        self.large_font_height = 22
        self.large_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/msttcorefonts/arial.ttf",
            self.large_font_height
        )
        self.second_line_offset = 30

        # Image border properties
        self.image_y = 13  # Vertical distance between top of display and top image border
        self.border_width = 7

    def create_frame_image(self, image, text_prompt, portrait_mode=False):
        """Generates the layout to display on the frame

        To quickly iterate on different types of layouts, see frame_composer_test.py
        """
        # If image is displayed in portrait mode, make it taller so that
        # there's room for the second line of the text prompt if it's needed
        base_image_height = (
            self.height + self.second_line_offset if portrait_mode else self.height
        )

        base_image = Image.new("RGB", (self.width, base_image_height), "white")
        draw = ImageDraw.Draw(base_image)

        # Add border around image
        draw.rectangle(
            xy=(
                (self.width - image.width) // 2 - self.border_width,
                self.image_y - self.border_width,
                image.width + (self.width - image.width) // 2 + self.border_width,
                self.image_y + self.border_width + image.height
            ),
           fill=(255, 255, 255),
           outline=(0, 0, 0)
        )

        # Check if the text prompt is too long for the display. If it is
        # then split it into two lines if the frame is also in portrait mode.
        text_prompt_split = text_prompt.split(" ")
        text_y = self.image_y + self.border_width + image.height
        if len(text_prompt) > MAX_CHARACTERS and portrait_mode:

            first_line = " ".join(text_prompt_split[:MAX_WORDS])
            second_line = " ".join(text_prompt_split[MAX_WORDS:])

            large_text_w, _ = draw.textsize(first_line, font=self.large_font)
            text_x = (self.width - large_text_w) // 2 - 10
            draw.text(
                xy=(text_x, text_y),
                text=f"{first_line}",
                font=self.large_font,
                fill=(0, 0, 0)
            )
            draw.text(
                xy=(text_x, text_y + 30),
                text=f"{second_line}",
                font=self.large_font,
                fill=(0, 0, 0)
            )
        else:
            large_text_w, _ = draw.textsize(text_prompt, font=self.large_font)
            text_x = (self.width - large_text_w) // 2 - 10
            draw.text(
                xy=(text_x, text_y),
                text=f"{text_prompt}",
                font=self.large_font,
                fill=(0, 0, 0)
            )

        # Add image to "frame"
        base_image.paste(
            im=image,
            box=((self.width - image.width) // 2, self.image_y)
        )
        return (
            base_image.
                rotate(90, fillcolor="white").
                resize(  # We resize to allow the final image to fit the ePaper display's dimensions
                    (
                        self.width,
                        base_image_height - self.second_line_offset
                    )
                )
            if portrait_mode else base_image
        )
