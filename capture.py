import cv2
import argparse
import time
import os
import Update_Model
import glob
import random
import eel

frequency = 2500
duration = 1000

eel.init('WD_INNOVATIVE')
emotions = ["angry", "happy", "sad", "neutral"]
fishface = cv2.face.FisherFaceRecognizer_create()
font = cv2.FONT_HERSHEY_SIMPLEX

parser = argparse.ArgumentParser(
    description="Options for emotions based music player(Updating the model)")
parser.add_argument(
    "--update", help="Call for taking new images and retraining the model.", action="store_true")
args = parser.parse_args()
facedict = {}
video_capture=cv2.VideoCapture(0)
facecascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")



def crop(clahe_image, face):
    for (x, y, w, h) in face:
        faceslice = clahe_image[y:y+h, x:x+w]
        faceslice = cv2.resize(faceslice, (350, 350))
        facedict["face%s" % (len(facedict)+1)] = faceslice
    return faceslice


def grab_face():
    ret, frame = video_capture.read()
    cv2.imwrite('test.jpg', frame)
    cv2.imwrite("images/main%s.jpg" % count, frame)
    gray = cv2.imread('test.jpg', 0)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_image = clahe.apply(gray)
    return clahe_image


def detect_face():
    clahe_image = grab_face()
    face = facecascade.detectMultiScale(clahe_image, scaleFactor=1.1, minNeighbors=15, minSize=(
        10, 10), flags=cv2.CASCADE_SCALE_IMAGE)
    if len(face) >= 1:
        faceslice = crop(clahe_image, face)
    else:
        print("No/Multiple faces detected!!, passing over the frame")


def checkForFolders(emotions):
    for emotion in emotions:
        if os.path.exists("dataset/%s" % emotion):
            pass
        else:
            os.makedirs("dataset/%s" % emotion)


def identify_emotions():
    prediction = []
    confidence = []

    for i in facedict.keys():
        pred, conf = fishface.predict(facedict[i])
        cv2.imwrite("images/%s.jpg" % i, facedict[i])
        prediction.append(pred)
        confidence.append(conf)
    output = emotions[max(set(prediction), key=prediction.count)]
    print("You seem to be %s" % output)
    facedict.clear()
    return output


count = 0

@eel.expose
def getEmotion():
    count = 0
    try:
        while count != 10:
            count = count+1
            detect_face()
            if count == 10:
                fishface.read("model.xml")

        return identify_emotions()

    except :
        print("Fail to detect face")



eel.start('main.html')
