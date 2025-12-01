import cv2  #helps me work with the videos 
import pytesseract  #helps my code read text from pictures
import requests     #for  talking to websites
import numpy as np  #helps crunch numbers

pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

def translate_text(text, target_lang='en'):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        'client': 'gtx',
        'sl': 'ja', #Japanese
        'tl': target_lang, #English by default
        'dt': 't',
        'q': text
    }
    response = requests.get(url, params=params)
    try:
        translated = response.json()
    except Exception:
        translated = ""
    return translated

def extract_text_region(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    denoised = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(denoised, 180, 255, cv2.THRESH_BINARY_INV) #THRESH_BINARY_INV makes dark areas white and light areas black.This is useful because subtitles are often white text on a dark background.
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    text_regions = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Use heuristic for subtitle area [adjust per cartoon]
        if w > 50 and h < 80 and y > frame.shape * 0.6:
            text_regions.append(frame[y:y+h, x:x+w])
    return text_regions

def annotate_frame(frame, text, box=None):
    position = (50, frame.shape - 60) if box is None else (box, box[12])
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,255), 2, cv2.LINE_AA)
    return frame

cap = cv2.VideoCapture('doremon_episode.mp4')

frame_rate = cap.get(cv2.CAP_PROP_FPS)
frame_count = 0
subtitle_buffer = ""

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame_count += 1

    text_regions = extract_text_region(frame)
    ocr_texts = []
    for r in text_regions:
        txt = pytesseract.image_to_string(r, lang='jpn')
        if txt.strip() and txt.strip() not in ocr_texts:
            ocr_texts.append(txt.strip())
    # Merge detected texts (for multiple lines)
    full_text = " ".join(ocr_texts)
    if full_text and full_text != subtitle_buffer:
        en_text = translate_text(full_text)
        subtitle_buffer = full_text
    else:
        en_text = ""

    if en_text:
        frame = annotate_frame(frame, en_text)

    cv2.imshow('Toonsletter_Translated', frame)
    if cv2.waitKey(int(1000/frame_rate)) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
