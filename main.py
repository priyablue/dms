'''Copyright (C) 2019 AS <parai@foxmail.com>'''
import os
import cv2
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-v', dest='video', default=0,
                    help='specify video sorce, e.g: http://192.168.1.101:4747/video')
parser.add_argument('-d', dest='detect', default='mtcnn',
                    help='which method to detect location of face, cv2 or mtcnn')
args = parser.parse_args()

cv2_root = os.path.dirname(os.path.realpath(cv2.__file__))
video = cv2.VideoCapture(args.video)

from models.facenet import predict as face_recognise
from models.emotion import predict as face_emotion
from models.drowsy import predict as face_drowsy
# from models.gaze import predict as gaze_direction
if(args.detect == 'cv2'):
    haar_face_cascade = cv2.CascadeClassifier('%s/data/haarcascade_frontalface_alt.xml'%(cv2_root))
else:
    from models.mtcnn import predict as face_detect

def cv2_face_detect(context):
    #https://www.superdatascience.com/blogs/opencv-face-detection
    frame = context['frame']
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    boxs = haar_face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    context['faces'] = [{'box':(x, y, w, h), 'frame':frame[y:y+h, x:x+w]} for (x, y, w, h) in boxs]

def visualize(context):
    frame = context['frame']
    for face in context['faces']:
        x, y, w, h = face['box']
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        if('faceid' in face):
            name,dis = face['faceid']
            cv2.putText(frame, '%s %.2f'%(name, dis), 
                    (x, y-20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 
                    1.0, (0, 0 ,255), thickness = 1, lineType = 2)
        if('emotion' in face):
            emotion,eprob = face['emotion']
            cv2.putText(frame, '%s %.2f'%(emotion, eprob), 
                    (x, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 
                    1.0, (0, 0 ,255), thickness = 1, lineType = 2)
        if('drowsy' in face):
            drowsy,prob,(ex1,ey1,ex2,ey2) = face['drowsy']
            if((ex1<ex2) and (ey1<ey2)):
                cv2.rectangle(frame, (x+ex1, y+ey1), (x+ex2, y+ey2), (0, 255, 0), 2)
    cv2.imshow('frame',frame)

def main():
    ret, frame = video.read()
    while(ret):
        context = { 'frame': frame }
        if(args.detect == 'cv2'):
            cv2_face_detect(context)
        else:
            face_detect(context)
        face_recognise(context)
        face_emotion(context)
        face_drowsy(context)
        visualize(context)
        if((cv2.waitKey(10)&0xFF) == ord('q')):
            break
        ret, frame = video.read()
    cap.release()
    cv2.destroyAllWindows()

if(__name__ == '__main__'):
    main()
