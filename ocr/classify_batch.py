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
# 🔥 Automatically detect the OCR folder path (works anywhere)
# ----------------------------------------------------------

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OCR_BASE_PATH = CURRENT_DIR

# ----------------------------------------------------------

def absolute(path):
    # 1. Absolute path → leave unchanged
    if os.path.isabs(path):
        return path

    # 2. If the file already exists inside CURRENT_DIR → do NOT prepend "ocr/"
    direct_path = os.path.join(CURRENT_DIR, path)
    if os.path.exists(direct_path):
        return direct_path

    # 3. Default case → prepend "ocr/"
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
    Classify a single image.
    Example:
        result = classify_image("test", "symbols.txt", "output.png")
    """

    model_name = absolute(model_name)
    symbols_file = absolute(symbols_file)
    image_file = absolute(image_file)

    # read symbols
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


def classify_folder(model_name, symbols_file, dest_folder):
    """
    Classify all images inside a folder.
    Example:
        classify_folder("test", "symbols.txt", "images")
    """

    model_name = absolute(model_name)
    symbols_file = absolute(symbols_file)
    dest_folder = absolute(dest_folder)

    # read symbols
    with open(symbols_file, 'r') as f:
        captcha_symbols = f.readline().strip()

    with tf.device('/cpu:0'):
        model = load_model(model_name)

    files = sorted(os.listdir(dest_folder))

    total = 0
    correct = 0

    for fname in files:
        if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        total += 1
        image_path = os.path.join(dest_folder, fname)

        predicted = classify_image(model_name, symbols_file, image_path)
        truth = os.path.splitext(fname)[0]

        if predicted == truth:
            correct += 1

        print(f"{fname} → predicted: {predicted} | truth: {truth}")

    accuracy = correct / total if total > 0 else 0

    print("\n==============================")
    print(f"Correct: {correct}/{total}")
    print(f"Accuracy: {accuracy:.4f}")
    print("==============================\n")


if __name__ == '__main__':

    # Single image example
    # result = classify_image("test", "symbols.txt", "output.png")
    # print("CAPTCHA Result:", result)

    # Folder classification example
    classify_folder("test", "symbols.txt", "test_data5")
