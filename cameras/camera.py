import cv2,os, urllib.request
import numpy as np
from django.conf import settings


class VideoCamera(object):
    """
    Class to handle IP cameras with opencv
    """
    def __init__(self, ip):
        """
        Init the camera with provided IP address, /mjpeg stands for url address,
        which is hosted by ESP camera
        :param ip:
        """
        # Wersja IP cam telefon
        #self.cam = 'http://' + str(ip) + ':8080' + '/video'
        # Wersja IP cam ESP
        self.cam = 'rtsp://' + str(ip) + '/mjpeg/1'
        self.video = cv2.VideoCapture(self.cam)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        """
        Process frames from camera and covert it to bytes frame by frame"
        :return:
        """
        success, image = self.video.read()
        frame_flip = cv2.flip(image, 1)
        ret, jpeg = cv2.imencode('.jpg', frame_flip)
        return jpeg.tobytes()

