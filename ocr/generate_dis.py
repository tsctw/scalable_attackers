import os
import random
import string
from PIL import Image, ImageDraw, ImageFont
from png_to_base64 import make_distorted_png
import base64
from io import BytesIO

FONT_PATH = "/Users/taosenchang/tcd_scalable_computing/project2/attackers_new/ocr/Kablammo.ttf"

def generate_captcha(word, output_path):
    width, height = 150, 60
    img = Image.new("RGB", (width, height), (255, 255, 255))
    d = ImageDraw.Draw(img)

    size = random.randint(28, 36)
    font = ImageFont.truetype(FONT_PATH, size)

    for _ in range(150):
        d.point(
            (random.randint(0, width-1), random.randint(0, height-1)),
            fill=(
                random.randint(100, 200),
                random.randint(100, 200),
                random.randint(100, 200)
            )
        )

    text_x = 40
    text_y = (height - size) // 2

    d.text(
        (text_x, text_y),
        word,
        font=font,
        fill=(48, 115, 240) 
    )
    b64_str = make_distorted_png(word)

     # Remove header like: "data:image/png;base64,"
    if "," in b64_str:
        b64_str = b64_str.split(",")[1]

    # Decode base64
    image_data = base64.b64decode(b64_str)
    img = Image.open(BytesIO(image_data))

    # Resize using Pillow new API
    img = img.resize((width, height), Image.Resampling.LANCZOS)

    img.save(output_path)


symbols_path = 'symbols.txt'
DEST = 'test_data5'

with open(symbols_path, 'r') as f:
    SYMBOLS = f.readline().strip()

if __name__ == "__main__":
    os.makedirs(DEST, exist_ok=True)
    for i in range(1000):
        s = "".join(random.choice(SYMBOLS) for _ in range(4))
        generate_captcha(s, f"{DEST}/{s}.png")
    

