import cv2
import os
from pyzbar import pyzbar
import pandas as pd
from datetime import datetime
import pyttsx3
import requests

class ISBNLookupError(Exception):
    """Raised when an ISBN lookup fails."""
    
    def __init__(self, isbn, message="Failed to look up ISBN"):
        self.isbn = isbn
        self.message = f"{message}: {isbn}"
        super().__init__(self.message)

def beep():
    #os.system("afplay /System/Library/Sounds/Glass.aiff")
    pass

def duplicated():
    #os.system("afplay /System/Library/Sounds/Funk.aiff")
    pass

def bad_book():
    #os.system("afplay /System/Library/Sounds/Basso.aiff")
    pass

engine = pyttsx3.init()

# Set speech rate (optional)
engine.setProperty('rate', 150)  # default is ~200

# Set voice (optional)
voices = engine.getProperty('voices')
for i, voice in enumerate(voices):
    print(i, voice.name, voice.id)

engine.setProperty('voice', voices[156].id)  # 0 = first voice, try 1 for alternate
engine.say("YOU have selected a voice")
engine.runAndWait()


#beep()
#duplicated()
#bad_book()

def say_title(book):
    title = book['Title']
    print("Say title", title)

    # Speak text
    engine.say(f"Book scanned {book['Title']}")
    engine.runAndWait()

def get_book_info(isbn):
    url = f'https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data'
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        key = f'ISBN:{isbn}'
        if key in data:
            book = data[key]
            title = book.get('title', '')
            authors = ', '.join([a['name'] for a in book.get('authors', [])])
            publish_year = book.get('publish_date', '')
            return {
                'ISBN': isbn,
                'Title': title,
                'Authors': authors,
                'PublishYear': publish_year
            }
        else:
            raise ISBNLookupError(isbn, message = "Not found")
    except Exception as e:
        raise ISBNLookupError(isbn, message = "ISBN General Exception")


# CSV file to store ISBNs
CSV_FILE = 'books.csv'

# Load existing data or create new
try:
    df = pd.read_csv(CSV_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=['ISBN', 'Timestamp'])

# Initialize webcam
cap = cv2.VideoCapture(0)  # 0 is usually the default webcam

print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect barcodes
    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:

        isbn = barcode.data.decode('utf-8')
        print("BAR CODE Scanned", isbn)
        # Only add if not already in CSV

        if isbn not in df['ISBN'].values:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df = pd.concat([df, pd.DataFrame({'ISBN':[isbn], 'Timestamp':[timestamp]})], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)
            print(f"Scanned ISBN: {isbn} at {timestamp}")
            try:
            
                book = get_book_info(isbn)
                title = book['Title']
                print(isbn, title)
                beep()
                say_title(book)

            except ISBNLookupError as e:
                bad_book()
                print("ISBN Lookup failed:", e)

        else:
            duplicated()


        # Draw rectangle and text
        x, y, w, h = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, isbn, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Show webcam feed
    cv2.imshow('ISBN Scanner', frame)

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


