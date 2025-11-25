import random, base64
from PIL import Image, ImageDraw, ImageFont
import io

FONT_PATH = "/Users/taosenchang/tcd_scalable_computing/project2/attackers_new/ocr/Kablammo.ttf"

def make_distorted_png(word):
    img = Image.new("RGB", (150, 60), (255, 255, 255))
    d = ImageDraw.Draw(img)

    size = random.randint(28, 36)
    font = ImageFont.truetype(FONT_PATH, size)

    # random noise
    for _ in range(150):
        d.point(
            (random.randint(0,149), random.randint(0,59)),
            fill=(random.randint(0,200),random.randint(0,200),random.randint(0,200))
        )

    d.text((40,10), word, font=font, fill=(48, 115, 240))

    buf = io.BytesIO()
    img.save(buf, format='webp')
    b64 = base64.b64encode(buf.getvalue()).decode('utf8')
    return f"data:image/png;base64,{b64}"