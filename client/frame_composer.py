from PIL import Image, ImageDraw, ImageFont


class FrameComposer:
    def __init__(self, width, height):

        # Display dimensions
        self.width = width
        self.height = height

        # Text prompt properties
        self.large_font_height = 22
        self.large_font = ImageFont.truetype("/usr/share/fonts/truetype/msttcorefonts/arial.ttf",
                                             self.large_font_height)

        # Image border properties
        self.image_y = 13  # Vertical distance between top of display and top image border
        self.border_width = 7

    def create_frame_image(self, image, text_prompt, portrait_mode=False):
        """Generates the layout to display on the frame

        To quickly iterate on different types of layouts, see frame_composer_test.py
        """
        base_image = Image.new("RGB", (self.width, self.height), "white")
        draw = ImageDraw.Draw(base_image)

        # Add border
        draw.rectangle(
            (
                (self.width - image.width) // 2 - self.border_width,
                self.image_y - self.border_width,
                image.width + (self.width - image.width) // 2 + self.border_width,
                self.image_y + self.border_width + image.height
            ),
           fill=(255, 255, 255),
           outline=(0, 0, 0)
        )

        # add text prompt
        large_text_w, large_text_h = draw.textsize(text_prompt, font=self.large_font)
        draw.text(
            (
                (self.width - large_text_w) // 2 - 10,
                self.image_y + self.border_width + image.height
            ),
            text=f"{text_prompt}",
            font=self.large_font,
            fill=(0, 0, 0)
        )

        # add image to "frame"
        base_image.paste(
            im=image,
            box=((self.width - image.width) // 2, self.image_y)
        )

        if portrait_mode:
            return base_image.rotate(90, fillcolor="white")
        return base_image
