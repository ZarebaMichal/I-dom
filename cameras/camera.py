import threading
import time
import cv2


class VideoCamera(object):
    """
    Class to handle IP cameras with opencv
    """
    def __new__(cls, *args, **kwargs):
        """
        Overwrite __new__ method to check if we opencv can connect to camera,
        if failed return None, else come to __init__
        :param args:
        :param kwargs:
        """
        obj = super(VideoCamera,cls).__new__(cls)
        obj._from_base_class = type(obj) == VideoCamera
        try:
            # dev version
            #cam = 'http://' + str(kwargs['ip']) + ':8080' + '/video'
            # prod version
            cam = 'rtsp://' + str(kwargs['ip']) + ':8554/mjpeg/1'
            video = cv2.VideoCapture(cam)
            if not video.isOpened() or video is None:
                return
        except cv2.error as e:
            print("cv2.error:", e)
        except Exception as e:
            print("Exception:", e)

        return obj

    def __init__(self, ip):
        """
        Init the camera with provided IP address, /mjpeg stands for url address,
        which is hosted by ESP camera
        :param ip:
        """
        # Wersja IP cam telefon
        #self.cam = 'http://' + str(ip) + ':8080' + '/video'
        # Wersja IP cam ESP
        self.cam = 'rtsp://' + str(ip) + ':8554/mjpeg/1'
        self.video = cv2.VideoCapture(self.cam)

        # Parameters of stream, buffer
        self.W, self.H = 640, 480
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, self.W)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, self.H)
        self.video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.video.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        # FPS = 1 / X
        # X = Desired FPS
        self.FPS = 1/30
        self.FPS_MS = int(self.FPS * 1000)

        (self.grabbed, self.frame) = self.video.read()
        self.started = False
        self.read_lock = threading.Lock()
        self.counter = 5
        self.counter_old = 0

        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

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
                time.sleep(self.FPS)
            else:
                return self.__exit__()

    def read(self):
        self.read_lock.acquire()
        if self.frame is None:
            return self.__exit__()
        frame = self.frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        self.read_lock.release()
        self.counter += 1
        self.counter_old = self.counter
        time.sleep(self.FPS)
        return frame

    def stop(self):
        self.started = False

    def __exit__(self):
        self.video.release()
        self.stop()
        self.__del__()

    def __del__(self):
        print('deleted')
