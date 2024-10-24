import pytesseract
from googletrans import Translator
from PIL import Image
import os
import time
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def clean_text(text):
    cleaned_text = re.sub(r'\n+', ' ', text)
    cleaned_text = re.sub(r'[^A-Za-z0-9\s\.\,\!\?]', '', cleaned_text)
    cleaned_text = cleaned_text.strip()
    return cleaned_text


def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang='eng') 
    return clean_text(text)


def translate_text(text):
    translator = Translator()
    try:
        translation = translator.translate(text, src='en', dest='pt')
        return translation.text
    except Exception as e:
        print(f"Error in translation: {e}")
        return text

def save_translation(original_text, translation):
    with open('translation.txt', 'a') as file:
        file.write(f"Original Text: {original_text}\n")
        file.write(f"Translation: {translation}\n")
        file.write("="*40 + "\n") 

def process_image(image_path):
    print(f"Processing image: {image_path}")
    extracted_text = extract_text_from_image(image_path)
    if extracted_text.strip():
        translation = translate_text(extracted_text)
        save_translation(extracted_text, translation)
        print(f"Translation saved: {translation}")
    else:
        print("No text found in the image.")

class ScreenshotMonitor(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".png"):
            time.sleep(1)
            process_image(event.src_path)


def monitor_folder(folder):
    event_handler = ScreenshotMonitor()
    observer = Observer()
    observer.schedule(event_handler, folder, recursive=False)
    observer.start()
    print(f"Monitoring folder: {folder}")
    try:
        while True:
            time.sleep(1) 
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    screenshot_folder = '/home/walter/Pictures/Screenshots'
    monitor_folder(screenshot_folder)
