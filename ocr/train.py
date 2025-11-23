# #!/usr/bin/env python3

# # python3 train.py --width 300 --height 150 --length 4 \
# #   --symbols symbols.txt --batch-size 32 --epochs 20 \
# #   --output-model test --train-dataset train_data --validate-dataset val_data

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

# # Build a Keras model given some parameters
# def create_model(captcha_length, captcha_num_symbols, input_shape, model_depth=5, module_size=2):
#   input_tensor = keras.Input(input_shape)
#   x = input_tensor
#   for i, module_length in enumerate([module_size] * model_depth):
#       for j in range(module_length):
#           x = keras.layers.Conv2D(32*2**min(i, 3), kernel_size=3, padding='same', kernel_initializer='he_uniform')(x)
#           x = keras.layers.BatchNormalization()(x)
#           x = keras.layers.Activation('relu')(x)
#       x = keras.layers.MaxPooling2D(2)(x)

#   x = keras.layers.Flatten()(x)
#   x = [keras.layers.Dense(captcha_num_symbols, activation='softmax', name='char_%d'%(i+1))(x) for i in range(captcha_length)]
#   model = keras.Model(inputs=input_tensor, outputs=x)

#   return model

# # A Sequence represents a dataset for training in Keras
# # In this case, we have a folder full of images
# # Elements of a Sequence are *batches* of images, of some size batch_size
# class ImageSequence(keras.utils.Sequence):
#     def __init__(self, directory_name, batch_size, captcha_length, captcha_symbols, captcha_width, captcha_height):
#         self.directory_name = directory_name
#         self.batch_size = batch_size
#         self.captcha_length = captcha_length
#         self.captcha_symbols = captcha_symbols
#         self.captcha_width = captcha_width
#         self.captcha_height = captcha_height

#         file_list = os.listdir(self.directory_name)
#         self.files = dict(zip(map(lambda x: x.split('.')[0], file_list), file_list))
#         self.used_files = []
#         self.count = len(file_list)

#     def __len__(self):
#         return int(numpy.floor(self.count / self.batch_size))

#     def __getitem__(self, idx):
#         if not self.files:
#             raise ValueError("Empty dataset: no files loaded. Please check data_dir path or loading logic.")

#         X = numpy.zeros((self.batch_size, self.captcha_height, self.captcha_width, 3), dtype=numpy.float32)
#         y = [numpy.zeros((self.batch_size, len(self.captcha_symbols)), dtype=numpy.uint8) for i in range(self.captcha_length)]

#         for i in range(self.batch_size):
#             random_image_label = random.choice(list(self.files.keys()))
#             random_image_file = self.files[random_image_label]


#             # We have to scale the input pixel values to the range [0, 1] for
#             # Keras so we divide by 255 since the image is 8-bit RGB
#             raw_data = cv2.imread(os.path.join(self.directory_name, random_image_file))
#             rgb_data = cv2.cvtColor(raw_data, cv2.COLOR_BGR2RGB)
#             processed_data = numpy.array(rgb_data) / 255.0
#             X[i] = processed_data

#             # We have a little hack here - we save captchas as TEXT_num.png if there is more than one captcha with the text "TEXT"
#             # So the real label should have the "_num" stripped out.

#             random_image_label = random_image_label.split('_')[0]

#             for j, ch in enumerate(random_image_label):
#                 y[j][i, :] = 0
#                 y[j][i, self.captcha_symbols.find(ch)] = 1

#         return X, tuple(y)

# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--width', help='Width of captcha image', type=int)
#     parser.add_argument('--height', help='Height of captcha image', type=int)
#     parser.add_argument('--length', help='Length of captchas in characters', type=int)
#     parser.add_argument('--batch-size', help='How many images in training captcha batches', type=int)
#     parser.add_argument('--train-dataset', help='Where to look for the training image dataset', type=str)
#     parser.add_argument('--validate-dataset', help='Where to look for the validation image dataset', type=str)
#     parser.add_argument('--output-model-name', help='Where to save the trained model', type=str)
#     parser.add_argument('--input-model', help='Where to look for the input model to continue training', type=str)
#     parser.add_argument('--epochs', help='How many training epochs to run', type=int)
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

#     if args.batch_size is None:
#         print("Please specify the training batch size")
#         exit(1)

#     if args.epochs is None:
#         print("Please specify the number of training epochs to run")
#         exit(1)

#     if args.train_dataset is None:
#         print("Please specify the path to the training data set")
#         exit(1)

#     if args.validate_dataset is None:
#         print("Please specify the path to the validation data set")
#         exit(1)

#     if args.output_model_name is None:
#         print("Please specify a name for the trained model")
#         exit(1)

#     if args.symbols is None:
#         print("Please specify the captcha symbols file")
#         exit(1)

#     captcha_symbols = None
#     with open(args.symbols) as symbols_file:
#         captcha_symbols = symbols_file.readline()

#     # physical_devices = tf.config.experimental.list_physical_devices('GPU')
#     # assert len(physical_devices) > 0, "No GPU available!"
#     # tf.config.experimental.set_memory_growth(physical_devices[0], True)

#     # with tf.device('/device:GPU:0'):
#     # with tf.device('/device:CPU:0'):
#     # with tf.device('/device:XLA_CPU:0'):
#         model = create_model(args.length, len(captcha_symbols), (args.height, args.width, 3))

#         if args.input_model is not None:
#             model.load_weights(args.input_model)

#         model.compile(loss='categorical_crossentropy',
#                       optimizer=keras.optimizers.Adam(1e-3, amsgrad=True),
#                       metrics=['accuracy'] * args.length)

#         model.summary()

#         training_data = ImageSequence(args.train_dataset, args.batch_size, args.length, captcha_symbols, args.width, args.height)
#         # X, y = training_data.__getitem__(0)
#         validation_data = ImageSequence(args.validate_dataset, args.batch_size, args.length, captcha_symbols, args.width, args.height)

#         callbacks = [keras.callbacks.EarlyStopping(patience=3),
#                      # keras.callbacks.CSVLogger('log.csv'),
#                      keras.callbacks.ModelCheckpoint(args.output_model_name+'.keras', save_best_only=False)]

#         # Save the model architecture to JSON
#         with open(args.output_model_name+".json", "w") as json_file:
#             json_file.write(model.to_json())

#         try:
#             # model.fit_generator(generator=training_data,
#             #                     validation_data=validation_data,
#             #                     epochs=args.epochs,
#             #                     callbacks=callbacks,
#             #                     use_multiprocessing=True)
            
#             model.fit(
#                 x=training_data, # 訓練資料 Sequence
#                 validation_data=validation_data, # 驗證資料 Sequence
#                 epochs=args.epochs,              # 訓練輪數
#                 callbacks=callbacks,             # EarlyStopping、ModelCheckpoint
#                 verbose=1                        # 顯示訓練進度條
#             )
#         except KeyboardInterrupt:
#             print('KeyboardInterrupt caught, saving current weights as ' + args.output_model_name+'_resume.keras')
#             model.save_weights(args.output_model_name+'_resume.keras')

# if __name__ == '__main__':
#     main()

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
        self.count = len(self.labels)

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

