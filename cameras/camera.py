
import threading
import cv2,os, urllib.request
import time
import numpy as np
#from threading import Thread, Lock
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
        self.cam = 'http://' + str(ip) + ':8080' + '/video'
        # Wersja IP cam ESP
        #self.cam = 'rtsp://' + str(ip) + ':8554/mjpeg/1'
        self.video = cv2.VideoCapture(self.cam)
        self.W, self.H = 640, 480
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, self.W)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, self.H)
        self.video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.video.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        # FPS = 1 / X
        # X = Desired FPS
        # self.FPS = 1/60
        # self.FPS_MS = int(self.FPS * 1000)
        (self.grabbed, self.frame) = self.video.read()
        self.started = False
        self.read_lock = threading.Lock()
        self.counter = 5
        self.counter_old = 0

    def start(self):
        if self.started:
            return None
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.deamon = True
        self.thread.start()
        return self

    def update(self):
        while self.started:
            if (self.counter_old - self.counter) < 10:
                (grabbed, frame) = self.video.read()
                self.read_lock.acquire()
                self.grabbed, self.frame = grabbed, frame
                self.read_lock.release()
                self.counter -= 1
            else:
                return self.__exit__()

    def read(self):
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        self.counter += 1
        self.counter_old = self.counter
        return frame

    def stop(self):
        self.started = False

    def __exit__(self):
        self.video.release()
        self.stop()
        self.__del__()

    def __del__(self):
        print('deleted')


    # def get_frame(self):
    #     """
    #     Process frames from camera and covert it to bytes frame by frame"
    #     :return:
    #     """
    #     success, image = self.video.read()
    #     frame_flip = cv2.flip(image, 1)
    #     ret, jpeg = cv2.imencode('.jpg', frame_flip)
    #     return jpeg.tobytes()

