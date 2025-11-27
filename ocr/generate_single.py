import os
import random
import string
from PIL import Image, ImageDraw, ImageFont
from png_to_base64 import make_captcha_char
import base64
from io import BytesIO
import uuid

FONT_PATH = "/Users/taosenchang/tcd_scalable_computing/project2/attackers_new/ocr/Kablammo.ttf"

def generate_captcha(ch, output_path):
    b64_str = make_captcha_char(ch)

     # Remove header like: "data:image/webp;base64,"
    if "," in b64_str:
        b64_str = b64_str.split(",")[1]

    # Decode base64
    image_data = base64.b64decode(b64_str)
    img = Image.open(BytesIO(image_data))

    # Resize using Pillow new API
    img = img.resize((60, 60), Image.Resampling.LANCZOS)

    img.save(output_path)


symbols_path = 'symbols.txt'
DEST = 'val_data_char'

with open(symbols_path, 'r') as f:
    SYMBOLS = f.readline().strip()

if __name__ == "__main__":
    os.makedirs(DEST, exist_ok=True)
    for i in range(5000):
        uid = str(uuid.uuid4())[0:8]
        ch = random.choice(SYMBOLS)

        generate_captcha(ch, f"{DEST}/{ch}_{uid}.png")

    

