import functools
import threading
import time
import asyncio
import websocket
import av
import json
import sys
import os
import numpy as np
import requests
from PIL import Image
from io import BytesIO
import base64
from collections import deque

try:
    import thread
except ImportError:
    import _thread as thread

# retico
from retico.modules.misty.mistyPy import Robot
from retico.core import abstract
from retico.core.visual.common import ImageIU

class MistyCameraVideoModule(abstract.AbstractProducingModule):
    @staticmethod
    def name():
        return "Misty II Camera Module"

    @staticmethod
    def description():
        return "A Module that tracks the Misty II Robot camera"

    @staticmethod
    def output_iu():
        return ImageIU

    def __init__(self, ip, pil=True, **kwargs):
        super().__init__(**kwargs)
        self.pil = pil
        self.ip = ip
        self.robot = Robot(ip)
        # self.robot.enable_avstream()
        # self.robot.stream_av()
        self.next_container = None
        self.queue = deque(maxlen=1)

    def process_iu(self, input_iu):
        pass

        # frame = self.next_container.decode(input_stream)
        # frame.pts = None
        # im = frame.to_ndarray()
        # if self.pil:
        #     im = Image.fromarray(im)
        # output_iu = self.create_iu(input_iu)
        # output_iu.set_image(im, 1, 1)
        # return output_iu
        # for frame in self.next_container.decode(input_stream):
        #     frame.pts = None
        #     sio.emit('audio', frame.to_ndarray().astype(np.float32).tostring())

    def start_video(self):
        print("connected, starting stream")
        stream_path = 'rtsp://{}:1936?framerate=1'.format(self.ip)
        self.next_container = av.open(stream_path)
        #input_stream = self.next_container.streams.get(audio=0)[0]
        for frame in self.next_container.decode(video=0):
            self.queue.append(frame)


    def av_thread(self):
        while True:
            if(len(self.queue) == 0):
                time.sleep(0.001)
                continue
            frame = self.queue.popleft()
            # frame.pts = None
            image = frame.to_image()
            # print(type(image))
            im = image.rotate(270)
            # rtotate
            if not self.pil:
                im = np.asarray(im)
            output_iu = self.create_iu(None)
            output_iu.set_image(im, 1, 1)
            self.append(output_iu)

    def setup(self):
        t = threading.Thread(target=self.av_thread)
        t.start()
        t = threading.Thread(target=self.start_video)
        t.start()        

# # robot_ip = '192.168.1.137'
# # robot = Robot(robot_ip)

# next_container = None



# @sio.event
# def connect():
#     global next_container
#     print("connected, starting stream")
#     stream_path = 'rtsp://{}:1936'.format(robot_ip)
#     next_container = av.open(stream_path)
#     input_stream = next_container.streams.get(audio=0)[0]
#     for frame in next_container.decode(input_stream):
#         frame.pts = None
#         sio.emit('audio', frame.to_ndarray().astype(np.float32).tostring())

# @sio.event
# def my_message(data):
#     print('message received with ', data)

# @sio.event
# def disconnect():
#     print('disconnected from server')


# sio.connect('http://192.168.1.135:5150')
# sio.wait()


