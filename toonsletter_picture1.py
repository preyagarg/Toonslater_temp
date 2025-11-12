import cv2
import pytesseract
import requests

# Path to your Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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

    # OCR to extract Japanese text
    text = pytesseract.image_to_string(gray, lang='jpn').strip()

    if text:
        print("Detected Japanese Text:")
        print(text)

        # Translate to English
        translated = translate_text(text)
        print("\nTranslated Text:")
        print(translated)

        # Write translated text as subtitle at bottom
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        color = (0, 255, 0)  # Green
        thickness = 2

        # Get image size to place subtitle at bottom
        (h, w) = image.shape[:2]
        y_pos = h - 20  # 20 pixels above bottom

        # Optional: draw a black rectangle for subtitle background
        cv2.rectangle(image, (0, y_pos - 30), (w, h), (0, 0, 0), -1)

        # Draw subtitle
        cv2.putText(image, translated, (10, y_pos), font, font_scale, color, thickness, cv2.LINE_AA)

    else:
        print("No Japanese text found.")

    # Save the image with subtitle
    cv2.imwrite(output_path, image)
    print(f"\n✅ Image saved to: {output_path}")

# Change to your actual image
input_image = 'japanese_text_image.png'
output_image = 'translated_subtitle_image.png'

process_image(input_image, output_image)
