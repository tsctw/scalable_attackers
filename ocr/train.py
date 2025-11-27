#!/usr/bin/env python3

# python3 train_simple.py --width 150 --height 60 --length 4 \
#   --batch-size 32 --epochs 20 \
#   --symbols symbols.txt --train-dataset train_data \
#   --validate-dataset val_data --output-model model_name

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import cv2
import numpy as np
import argparse
import tensorflow as tf
import tensorflow.keras as keras

# --------------------------
# Build custom multi-output CNN
# --------------------------
def create_model(captcha_length, captcha_num_symbols, input_shape, model_depth=4, module_size=2):
    input_tensor = keras.Input(input_shape)
    x = input_tensor

    # CNN Feature Extractor
    for i in range(model_depth):
        for j in range(module_size):
            x = keras.layers.Conv2D(
                filters=32 * (2 ** min(i, 3)), 
                kernel_size=3,
                padding="same",
                kernel_initializer="he_uniform"
            )(x)
            x = keras.layers.BatchNormalization()(x)
            x = keras.layers.Activation("relu")(x)
        x = keras.layers.MaxPooling2D(pool_size=2)(x)

    x = keras.layers.Flatten()(x)

    # Multi-head classifier: one output per character
    outputs = []
    for i in range(captcha_length):
        outputs.append(
            keras.layers.Dense(
                captcha_num_symbols, 
                activation="softmax", 
                name=f"char_{i+1}"
            )(x)
        )

    return keras.Model(inputs=input_tensor, outputs=outputs)


# --------------------------
# Custom DataLoader for PIL CAPTCHA format
# --------------------------
class SimpleImageSequence(keras.utils.Sequence):
    def __init__(self, directory, batch_size, captcha_length, symbols, width, height):
        self.directory = directory
        self.batch_size = batch_size
        self.captcha_length = captcha_length
        self.symbols = symbols
        self.width = width
        self.height = height

        file_list = os.listdir(directory)
        self.files = {}

        for fname in file_list:
            if not fname.lower().endswith(".png"):
                continue
            label = fname.split(".")[0].split("_")[0]
            self.files[label] = fname

        self.labels = list(self.files.keys())
        self.count = len(file_list)

    def __len__(self):
        return self.count // self.batch_size

    def __getitem__(self, idx):
        X = np.zeros((self.batch_size, self.height, self.width, 3), dtype=np.float32)
        y = [np.zeros((self.batch_size, len(self.symbols)), dtype=np.uint8)
             for _ in range(self.captcha_length)]

        for i in range(self.batch_size):
            label = np.random.choice(self.labels)
            fname = self.files[label]

            img = cv2.imread(os.path.join(self.directory, fname))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (self.width, self.height))
            img = img.astype(np.float32) / 255.0

            X[i] = img

            # Process label
            for k, ch in enumerate(label):
                y[k][i, self.symbols.find(ch)] = 1

        return X, tuple(y)


# --------------------------
# Training Script
# --------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--length", type=int, required=True)
    parser.add_argument("--batch-size", type=int, required=True)
    parser.add_argument("--epochs", type=int, required=True)
    parser.add_argument("--train-dataset", type=str, required=True)
    parser.add_argument("--validate-dataset", type=str, required=True)
    parser.add_argument("--output-model", type=str, required=True)
    parser.add_argument("--symbols", type=str, required=True)
    parser.add_argument("--input-model", type=str, default=None)
    args = parser.parse_args()

    # Load symbols
    with open(args.symbols, "r") as f:
        captcha_symbols = f.readline().strip()

    # Build model
    model = create_model(
        captcha_length=args.length,
        captcha_num_symbols=len(captcha_symbols),
        input_shape=(args.height, args.width, 3)
    )

    # Continue training?
    if args.input_model:
        model.load_weights(args.input_model)
        print(f"Loaded weights from: {args.input_model}")

    model.compile(
        loss="categorical_crossentropy",
        optimizer=keras.optimizers.Adam(1e-3),
        metrics=["accuracy"] * args.length
    )

    model.summary()

    # Data Generators
    train_data = SimpleImageSequence(
        args.train_dataset,
        args.batch_size,
        args.length,
        captcha_symbols,
        args.width,
        args.height
    )

    val_data = SimpleImageSequence(
        args.validate_dataset,
        args.batch_size,
        args.length,
        captcha_symbols,
        args.width,
        args.height
    )

    callbacks = [
        keras.callbacks.EarlyStopping(patience=4, restore_best_weights=True),
        keras.callbacks.ModelCheckpoint(args.output_model + ".keras", save_best_only=True)
    ]

    # Save architecture
    with open(args.output_model + ".json", "w") as f:
        f.write(model.to_json())

    model.fit(
        train_data,
        validation_data=val_data,
        epochs=args.epochs,
        callbacks=callbacks,
        verbose=1
    )

    print("Training finished! Model saved.")

if __name__ == "__main__":
    main()

