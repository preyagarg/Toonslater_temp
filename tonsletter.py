import cv2  #helps me work with the videos 
import pytesseract  #helps my code read text from pictures
import requests     #for  talking to websites
import numpy as np  #helps crunch numbers

# Setup: Tesseract must have Japanese language data installed.
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  #  where my text-reading robot (Tesseract) lives inside my computer.

def translate_text(text, target_lang='en'):  #defines a function here which takes input of text to be converted and langauge in which it has to be converted
    url = "https://translate.googleapis.com/translate_a/single"  #his is the address of Google's free translation service.
    params = {
        'client': 'gtx',     # Just a required tag (stands for Google Translate Client)
        'sl': 'ja',          # sl = source language = Japanese
        'tl': target_lang,   # tl = target language = English by default
        'dt': 't',           # We want 'translated text'
        'q': text            # The actual Japanese sentence we're sending
    }
    response = requests.get(url, params=params)  #This sends a GET request to Google with our parameters.
    try:
        translated = response.json() #Google sends back data in JSON format (a structured text format).
    except Exception:
        translated = ""  #If something goes wrong (like no internet, or wrong input), it won't crash.Instead, it just returns an empty string.
    return translated

def extract_text_region(frame):   #function that takes a single video frame and tries to find areas that look like text
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  #The frame is in color (BGR format), but we change it to black & white (grayscale) to simplify processing.Text detection works better in grayscale.
    denoised = cv2.GaussianBlur(gray, (5, 5), 0)  #cleaner detection of text regions, fewer false areas.Using GaussianBlur is like wiping the foggy window a bit — the text becomes clearer.
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
    # Animate overlay—box can be None for default
    position = (50, frame.shape - 60) if box is None else (box, box[12])
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,255), 2, cv2.LINE_AA)
    return frame

# Video Processing Setup
cap = cv2.VideoCapture('doremon_episode.mp4')  # or webcam/live stream

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
        # Translate
        en_text = translate_text(full_text)
        subtitle_buffer = full_text
    else:
        en_text = ""

    # Animate and synchronize subtitles
    if en_text:
        frame = annotate_frame(frame, en_text)

    cv2.imshow('Toonsletter_Translated', frame)
    if cv2.waitKey(int(1000/frame_rate)) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
