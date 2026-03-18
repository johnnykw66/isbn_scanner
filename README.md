# ISBN Scanner

Scan ISBN books with web camera and store in a CSV file

## Once only

mkdir book_scanner

cd book_scanner

python -m venv .


## Then in another terminal shell

cd ~/book_scanner

source ~/bin/activate

python -m pip install requests pandas pyzbar opencv-python pyttsx3



## Then to run book scanner -

python scan.py

## Hold up ISBN books to camera.
