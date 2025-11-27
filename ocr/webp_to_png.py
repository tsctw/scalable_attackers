from PIL import Image
import os

def webp_to_png_folder(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".webp"):
            input_path = os.path.join(input_folder, filename)

            # 讀取 webp
            img = Image.open(input_path).convert("RGBA")

            # 輸出 png（同名, 副檔名改 png）
            base = os.path.splitext(filename)[0]
            output_path = os.path.join(output_folder, base + ".png")

            img.save(output_path, "PNG")
            print("Converted:", filename, "→", base + ".png")

    print("\nDone! All WebP converted.")


if __name__ == "__main__":
    webp_to_png_folder("test_data6", "test_data7")