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
        'sl': 'ja',           # Source language: Japanese
        'tl': target_lang,    # Target language
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

def extract_text_regions(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    denoised = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(denoised, 180, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    text_regions = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 40 and h > 20:  # filter small boxes
            text_regions.append((x, y, w, h))

    return text_regions

def process_video(video_path, output_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error opening video file.")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_num = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        text_regions = extract_text_regions(frame)

        for (x, y, w, h) in text_regions:
            roi = frame[y:y+h, x:x+w]
            text = pytesseract.image_to_string(roi, lang='jpn').strip()

            if text:
                translated = translate_text(text)
                if translated:
                    cv2.putText(frame, translated, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                                0.7, (0, 255, 0), 2, cv2.LINE_AA)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        out.write(frame)
        frame_num += 1
        print(f"Processed frame {frame_num}")

    cap.release()
    out.release()
    print(f"\n✅ Video saved with subtitles to: {output_path}")

# Change to your actual video file
input_video = "doremon_episode.mp4"
output_video = "translated_subtitles_output.mp4"

process_video(input_video, output_video)
