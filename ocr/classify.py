# #!/usr/bin/env python3

# # python3 classify.py  --model-name test --captcha-dir images --output \
# #   stuff.txt --symbols symbols.txt

# import warnings
# warnings.filterwarnings("ignore", category=FutureWarning)
# warnings.filterwarnings("ignore", category=DeprecationWarning)

# import os
# import cv2
# import numpy
# import string
# import random
# import argparse
# import tensorflow as tf
# import tensorflow.keras as keras

# def decode(characters, y):
#     y = numpy.argmax(numpy.array(y), axis=2)[:,0]
#     return ''.join([characters[x] for x in y])

# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--model-name', help='Model name to use for classification', type=str)
#     parser.add_argument('--captcha-dir', help='Where to read the captchas to break', type=str)
#     parser.add_argument('--output', help='File where the classifications should be saved', type=str)
#     parser.add_argument('--symbols', help='File with the symbols to use in captchas', type=str)
#     args = parser.parse_args()

#     if args.model_name is None:
#         print("Please specify the CNN model to use")
#         exit(1)

#     if args.captcha_dir is None:
#         print("Please specify the directory with captchas to break")
#         exit(1)

#     if args.output is None:
#         print("Please specify the path to the output file")
#         exit(1)

#     if args.symbols is None:
#         print("Please specify the captcha symbols file")
#         exit(1)

#     symbols_file = open(args.symbols, 'r')
#     captcha_symbols = symbols_file.readline().strip()
#     symbols_file.close()

#     print("Classifying captchas with symbol set {" + captcha_symbols + "}")

#     with tf.device('/cpu:0'):
#         with open(args.output, 'w') as output_file:
#             json_file = open(args.model_name+'.json', 'r')
#             loaded_model_json = json_file.read()
#             json_file.close()
#             model = keras.models.model_from_json(loaded_model_json)
#             model.load_weights(args.model_name+'.keras')
#             model.compile(loss='categorical_crossentropy',
#                           optimizer=keras.optimizers.Adam(1e-3, amsgrad=True),
#                           metrics=['accuracy'])
   
#             files = sorted(os.listdir(args.captcha_dir))
#             print(files)
#             for x in files:
#                 # print(x)
#                 # load image and preprocess it
#                 raw_data = cv2.imread(os.path.join(args.captcha_dir, x))
#                 rgb_data = cv2.cvtColor(raw_data, cv2.COLOR_BGR2RGB)
#                 image = numpy.array(rgb_data) / 255.0
#                 (c, h, w) = image.shape
#                 image = image.reshape([-1, c, h, w])
#                 prediction = model.predict(image)
#                 output_file.write(x + "," + decode(captcha_symbols, prediction) + "\n")

#                 print('Classified ' + x)

# if __name__ == '__main__':
#     main()

#!/usr/bin/env python3

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import cv2
import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
import os

# ----------------------------------------------------------
# 🔥 自動找出 ocr 資料夾路徑（不管在哪執行都有效）
# ----------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OCR_BASE_PATH = CURRENT_DIR

# ----------------------------------------------------------

def absolute(path):
    """
    將相對路徑自動指向 OCR_BASE_PATH，除非：
    1. 已經在 OCR_BASE_PATH 裡
    2. 已經是絕對路徑
    """

    # 1. 絕對路徑 → 不動
    if os.path.isabs(path):
        return path

    # 2. 如果目前檔案已經在 OCR_BASE_PATH 中存在 → 不要再加 ocr/
    direct_path = os.path.join(CURRENT_DIR, path)
    if os.path.exists(direct_path):
        return direct_path

    # 3. 一般情況 → 加上 ocr/
    return os.path.join(OCR_BASE_PATH, path)


def decode(characters, y):
    y = np.argmax(np.array(y), axis=2)[:, 0]
    return ''.join([characters[x] for x in y])

def load_model(model_name):
    json_file = open(model_name + '.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()

    model = keras.models.model_from_json(loaded_model_json)
    model.load_weights(model_name + '.keras')

    model.compile(
        loss='categorical_crossentropy',
        optimizer=keras.optimizers.Adam(1e-3, amsgrad=True),
        metrics=['accuracy']
    )
    return model

def classify_image(model_name, symbols_file, image_file):
    """
    你呼叫時只要給『檔案名』即可。
    ex: classify_image("test", "symbols.txt", "output.png")
    """

    # 自動補上 ocr/xxx
    model_name = absolute(model_name)
    symbols_file = absolute(symbols_file)
    image_file = absolute(image_file)

    # 讀 symbols
    with open(symbols_file, 'r') as f:
        captcha_symbols = f.readline().strip()

    with tf.device('/cpu:0'):
        model = load_model(model_name)

    raw = cv2.imread(image_file)
    if raw is None:
        raise ValueError("Image not found: " + image_file)

    rgb = cv2.cvtColor(raw, cv2.COLOR_BGR2RGB)
    img = np.array(rgb) / 255.0
    img = img.reshape([-1, img.shape[0], img.shape[1], img.shape[2]])

    pred = model.predict(img)
    return decode(captcha_symbols, pred)

if __name__ == '__main__':
    result = classify_image("test", "symbols.txt", "output.png")
    print("CAPTCHA Result:", result)