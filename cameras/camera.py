import cv2,os, urllib.request
import numpy as np
from django.conf import settings


class VideoCamera(object):
    def __init__(self):
        self.cam = 'http://192.168.18.7:8080/video'
        self.video = cv2.VideoCapture(self.cam)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        frame_flip = cv2.flip(image, 1)
        ret, jpeg = cv2.imencode('.jpg', frame_flip)
        return jpeg.tobytes()

