"""
Code for quickly experimenting with different display layouts
"""

from PIL import Image, ImageDraw, ImageFont

text_prompt = "The quick brown fox jumped over the lazy dogs to cross the river"
#text_prompt = "The quick brown fox jumped over"
#text_prompt = "a cat in the hat saw a fat bat on a mat"
#text_prompt = "A painting of a robot in the style of Van Gogh"

# Display width and height
width = 600
height = 448

# Check length of text prompt
max_characters = 40  # In case a text prompt contains short words, use number of characters to determine the split
max_words = 7
portrait_mode = True

image_width = 390
image_height = 390

border_width = 7
image_y = 15  # Vertical distance from the top of display

large_font_height = 25
large_font = ImageFont.truetype("/Users/palermopenano/Downloads/Arial.ttf", large_font_height)

# If image is displayed in portrait mode, make it taller so that
# there's room for the second line of the text prompt if it's needed
if portrait_mode:
    height += 30

base_image = Image.new("RGB", (width, height), "white")
draw = ImageDraw.Draw(base_image)

rectangle_boundaries = (
    (width - image_width) // 2 - border_width,                # x0
    image_y - border_width,                                   # y0
    image_width + (width - image_width) // 2 + border_width,  # x1
    image_y + border_width + image_height                     # y1
)
draw.rectangle(rectangle_boundaries, fill=(255,255,255), outline=(0,0,0))

text_prompt_split = text_prompt.split(" ")
if len(text_prompt) > max_characters and portrait_mode:

    first_line = " ".join(text_prompt_split[:max_words])
    second_line = " ".join(text_prompt_split[max_words:])

    large_text_w, _ = draw.textsize(first_line, font=large_font)
    text_x = (width - large_text_w) // 2 - 10
    text_y = image_y + border_width + image_height
    draw.text(
        xy=(text_x, text_y),
        text=f"{first_line}",
        font=large_font,
        fill=(0, 0, 0)
    )
    draw.text(
        xy=(text_x, text_y + 30),
        text=f"{second_line}",
        font=large_font,
        fill=(0, 0, 0)
    )
    base_image = base_image.resize((600, 448))
    base_image.show()
    print(base_image.size)
    base_image.rotate(90, fillcolor="white").show()
else:
    large_text_w, _ = draw.textsize(text_prompt, font=large_font)
    text_x = (width - large_text_w) // 2 - 10
    text_y = image_y + border_width + image_height
    draw.text(
        xy=(text_x, text_y),
        text=f"{text_prompt}",
        font=large_font,
        fill=(0, 0, 0)
    )
    base_image.show()

