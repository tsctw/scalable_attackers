# #!/usr/bin/env python3
# # python3 generate.py --width 300 --height 150 --length 4 \
# #    --symbols symbols.txt --count 20000 --output-dir train_data

# import os
# import numpy
# import random
# import string
# import cv2
# import argparse
# import captcha.image

# FONT = "/Users/taosenchang/tcd_scalable_computing/project2/attackers_new/ocr/Kablammo.ttf"

# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--width', help='Width of captcha image', type=int)
#     parser.add_argument('--height', help='Height of captcha image', type=int)
#     parser.add_argument('--length', help='Length of captchas in characters', type=int)
#     parser.add_argument('--count', help='How many captchas to generate', type=int)
#     parser.add_argument('--output-dir', help='Where to store the generated captchas', type=str)
#     parser.add_argument('--symbols', help='File with the symbols to use in captchas', type=str)
#     args = parser.parse_args()

#     if args.width is None:
#         print("Please specify the captcha image width")
#         exit(1)

#     if args.height is None:
#         print("Please specify the captcha image height")
#         exit(1)

#     if args.length is None:
#         print("Please specify the captcha length")
#         exit(1)

#     if args.count is None:
#         print("Please specify the captcha count to generate")
#         exit(1)

#     if args.output_dir is None:
#         print("Please specify the captcha output directory")
#         exit(1)

#     if args.symbols is None:
#         print("Please specify the captcha symbols file")
#         exit(1)

#     captcha_generator = captcha.image.ImageCaptcha(width=args.width, height=args.height, fonts=[FONT])

#     symbols_file = open(args.symbols, 'r')
#     captcha_symbols = symbols_file.readline().strip()
#     symbols_file.close()

#     print("Generating captchas with symbol set {" + captcha_symbols + "}")

#     if not os.path.exists(args.output_dir):
#         print("Creating output directory " + args.output_dir)
#         os.makedirs(args.output_dir)

#     for i in range(args.count):
#         random_str = ''.join([random.choice(captcha_symbols) for j in range(args.length)])
#         image_path = os.path.join(args.output_dir, random_str+'.png')
#         if os.path.exists(image_path):
#             version = 1
#             while os.path.exists(os.path.join(args.output_dir, random_str + '_' + str(version) + '.png')):
#                 version += 1
#             image_path = os.path.join(args.output_dir, random_str + '_' + str(version) + '.png')

#         image = numpy.array(captcha_generator.generate_image(random_str))
#         cv2.imwrite(image_path, image)

# if __name__ == '__main__':
#     main()

import os
import random
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/Users/taosenchang/tcd_scalable_computing/project2/attackers_new/ocr/Kablammo.ttf"

def generate_captcha(word, output_path):
    # 1. 建立白底圖片
    width, height = 150, 60
    img = Image.new("RGB", (width, height), (255, 255, 255))
    d = ImageDraw.Draw(img)

    # 2. 隨機字體大小
    size = random.randint(28, 36)
    font = ImageFont.truetype(FONT_PATH, size)

    # 3. 畫隨機噪音
    for _ in range(150):
        d.point(
            (random.randint(0, width-1), random.randint(0, height-1)),
            fill=(
                random.randint(100, 200),
                random.randint(100, 200),
                random.randint(100, 200)
            )
        )

    # 4. 文字位置（固定靠左）
    text_x = 40
    text_y = (height - size) // 2  # 垂直置中

    d.text(
        (text_x, text_y),
        word,
        font=font,
        fill=(48, 115, 240)  # 淡藍色
    )

    # 5. 儲存
    img.save(output_path)


symbols_path = 'symbols.txt'
DEST = 'val_data'

# 讀取 symbols
with open(symbols_path, 'r') as f:
    SYMBOLS = f.readline().strip()

# 測試
if __name__ == "__main__":
    os.makedirs(DEST, exist_ok=True)
    for i in range(5000):
        s = "".join(random.choice(SYMBOLS) for _ in range(4))
        generate_captcha(s, f"{DEST}/{s}.png")

