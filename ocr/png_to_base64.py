import random, base64
from PIL import Image, ImageDraw, ImageFont
import io

FONT_PATH = "/Users/taosenchang/tcd_scalable_computing/project2/attackers_new/ocr/Kablammo.ttf"

CHALLENGES = {}
MAX_WORD_COUNT = 4
SIZE = 60

def make_letter_tile(letter, color=(0,0,0)):
    img = Image.new("RGBA",(SIZE, SIZE),(255,255,255,0))

    # letter interior mask
    mask = Image.new("L",(SIZE, SIZE),0)
    dmask = ImageDraw.Draw(mask)
    font = ImageFont.truetype(FONT_PATH, 42)

    dmask.text((20,0), letter, font=font, fill=255)

    # fill interior with granular noise
    for _ in range(4000):
        x = random.randint(0, SIZE-1)
        y = random.randint(0, SIZE-1)

        if mask.getpixel((x,y)) > 180:
            img.putpixel(
                (x,y),
                (
                    min(color[0] + random.randint(-20,20),255),
                    min(color[1] + random.randint(-20,20),255),
                    min(color[2] + random.randint(-20,20),255),
                    240
                )
            )

    return img

def make_captcha_media(word, animated=True):

    FRAMES = 4
    DURATION = 120

    frames = []

    for _ in range(FRAMES):

        final = Image.new("RGB", (260, 80), (255,255,255))
        d = ImageDraw.Draw(final)

        # paste tiles
        x = 10
        for ch in word:
            tile = make_letter_tile(ch)
            final.paste(tile, (x, random.randint(0,25)), tile)
            x += SIZE

        frames.append(final)

    buf = io.BytesIO()
    
    # static WEBP
    if not animated:
        frames[0].save(buf, format="WEBP")
    else:
        # animated GIF
        frames[0].save(
            buf,
            format='webp',
            save_all=True,
            append_images=frames[1:],
            duration=DURATION,
            optimize=False,
            loop=0
        )

    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()