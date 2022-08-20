"""
Code for quickly experimenting with different display layouts
"""

from PIL import Image, ImageDraw, ImageFont

text_prompt = "A park in Monet"

# Display width and height
width = 600; height = 448

image_width = 390
image_height = 390

border_width = 7
image_y = 15  # Vertical distance between top of display and top image border

large_font_height = 25

large_font = ImageFont.truetype("/Users/palermopenano/Downloads/Arial.ttf", large_font_height)

base_image = Image.new("RGB", (width, height), "white")
draw = ImageDraw.Draw(base_image)

rectangle_boundaries = (
    (width - image_width) // 2 - border_width, 
    image_y - border_width,
    image_width + (width - image_width) // 2 + border_width, 
    image_y + border_width + image_height
)
draw.rectangle(rectangle_boundaries, fill=(255,255,255), outline=(0,0,0))


large_text_w, large_text_h = draw.textsize(text_prompt, font=large_font)
draw.text(
    (
        (width - large_text_w) // 2 - 10,
        image_y + border_width + image_height
    ),
    text=f"\"{text_prompt}\"",
    font=large_font,
    fill=(0, 0, 0)
)

base_image.show()

