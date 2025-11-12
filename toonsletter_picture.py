import cv2
import pytesseract
import requests
import numpy as np

# Path to your Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def translate_text(text, target_lang='en'):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        'client': 'gtx',
        'sl': 'ja',           # Source: Japanese
        'tl': target_lang,    # Target: English
        'dt': 't',
        'q': text
    }
    try:
        response = requests.get(url, params=params)
        result = response.json()
        translated = ''.join([part[0] for part in result[0]])
        return translated
    except Exception as e:
        print("Translation error:", e)
        return ""

def process_image(image_path, output_path):
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print("Failed to load image.")
        return

    h, w, _ = image.shape

    # Extract text using Tesseract
    text = pytesseract.image_to_string(image, lang='jpn').strip()

    if text:
        print("Japanese Text Found:\n", text)
        translated = translate_text(text)
        print("Translated:\n", translated)

        # Optional: draw a black rectangle at the bottom for subtitle background
        cv2.rectangle(image, (0, h - 50), (w, h), (0, 0, 0), -1)

        # Put translated subtitle
        cv2.putText(
            image,
            translated,
            (10, h - 15),  # 10px from left, 15px from bottom
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )
    else:
        print("No Japanese text detected.")

    # Save the output
    cv2.imwrite(output_path, image)
    print(f"\n✅ Saved translated image to: {output_path}")

# ==== RUN THE FUNCTION ====
input_image = 'japanese_text_image.png'        # Replace with your image path
output_image = 'translated_output_image.png'

process_image(input_image, output_image)
