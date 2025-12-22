import os
from dotenv import load_dotenv
load_dotenv()
import cv2
import pytesseract
import requests

pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")

# Translate Japanese to English
def translate_text(text, target_lang='en'):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        'client': 'gtx',
        'sl': 'ja',
        'tl': target_lang,
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

# Process a single image
def process_image(image_path, output_path):
    image = cv2.imread(image_path)

    # Convert to grayscale for better OCR
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    text = pytesseract.image_to_string(gray, lang='jpn').strip()

    if text:
        print("Detected Japanese Text:")
        print(text)

        translated = translate_text(text)
        print("\nTranslated Text:")
        print(translated)

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        color = (0, 255, 0)  # Green
        thickness = 1

        (h, w) = image.shape[:2]
        y_pos = h - 20

        cv2.rectangle(image, (0, y_pos - 30), (w, h), (0, 0, 0), -1)
        lines = translated.split('\n')

        line_height = 40
        padding = 20
        (h, w) = image.shape[:2]
        extra_height = ((len(lines)-1) * line_height) + padding
        new_image = cv2.copyMakeBorder(image,0,extra_height,0,0,cv2.BORDER_CONSTANT,value=(0, 0, 0))
        start_y = h


        for i, line in enumerate(lines):
            y = start_y + (i * line_height)

            cv2.putText(new_image,line,(10, y),font,font_scale,color,thickness,cv2.LINE_AA)
    else:
        print("No Japanese text found.")

    cv2.imwrite(output_path, new_image)
    print(f"\nImage saved to: {output_path}")

input_image = 'japanese_text_image.png'
output_image = 'translated_subtitle_image.png'

process_image(input_image, output_image)