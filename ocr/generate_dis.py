import os
import random
import string
from PIL import Image, ImageDraw, ImageFont
from png_to_base64 import make_captcha_media
import base64
from io import BytesIO

FONT_PATH = "/Users/taosenchang/tcd_scalable_computing/project2/attackers_new/ocr/Kablammo.ttf"

def generate_captcha(word, output_path):
    
    b64_str = make_captcha_media(word)

     # Remove header like: "data:image/webp;base64,"
    if "," in b64_str:
        b64_str = b64_str.split(",")[1]

    # Decode base64
    image_data = base64.b64decode(b64_str)
    img = Image.open(BytesIO(image_data))

    # Resize using Pillow new API
    img = img.resize((260, 80), Image.Resampling.LANCZOS)

    img.save(output_path)


symbols_path = 'symbols.txt'
DEST = 'train_data'

with open(symbols_path, 'r') as f:
    SYMBOLS = f.readline().strip()

if __name__ == "__main__":
    os.makedirs(DEST, exist_ok=True)
    for i in range(50000):
        s = "".join(random.choice(SYMBOLS) for _ in range(4))
        generate_captcha(s, f"{DEST}/{s}.png")
    

