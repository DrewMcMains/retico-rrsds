import threading
import time

# set vars before importing modules
import os
import sys

os.environ['GOOGLE_APPLICATION_CREDENTIALS']='/home/slimlab/retico_v2/creds.json'
os.environ['PYOD'] = '/home/slimlab/retico_v2/pyopendial'

prefix = '/home/slimlab/retico_v2/'
sys.path.append(prefix+'retico_core')
sys.path.append(prefix+'retico_opendialdm')
sys.path.append(prefix+'retico_wacnlu')
sys.path.append(prefix+'retico_mistyrobot')
sys.path.append(prefix+'retico_clip')
sys.path.append(prefix+'retico_vision')
sys.path.append(prefix+'retico_yolov8')
sys.path.append(prefix+'retico_whisperasr')
sys.path.append(prefix+'retico_respeakermic')
sys.path.append(prefix+'retico_googleasr')

import warnings
warnings.filterwarnings('ignore')
import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)

# retico
from retico_core.audio import MicrophoneModule
from retico_core.audio import *
from retico_core.debug import DebugModule
from retico_googleasr.googleasr import GoogleASRModule
from retico_opendialdm.dm import OpenDialModule
from retico_core.text import IncrementalizeASRModule
from retico_wacnlu.words_as_classifiers import WordsAsClassifiersModule
from retico_vision.vision import ImageCropperModule
from retico_mistyrobot.misty_camera import MistyCameraModule
from retico_mistyrobot.misty_refer import MistyReferModule
from retico_mistyrobot.misty_state import MistyStateModule
from retico_clip.clip import ClipObjectFeatures
from retico_yolov8.yolov8 import Yolov8
from retico_respeakermic.respeaker import RespeakerMicrophoneModule
# show_audio_devices()

domain_dir = '/home/slimlab/retico_v2/data/misty/dm/dialogue.xml'
wac_dir = '/home/slimlab/retico_v2/data/wac'
misty_ip = '192.168.0.155' # black misty
# misty_ip = '192.168.0.101' # white misty
respeaker = '192.168.0.152:8000'

opendial_variables = [#'face_count', # 
                        'num_objs', # ObjectDetector
                        'exploring', # MistyReferModule
                        'aligned', #  MistyReferModule
                        'word_to_find', # WordsAsClassifiersModule
                        'best_object', # WordsAsClassifiersModule
                        'obj_confidence'] # WordsAsClassifiersModule

#
# INSTANTIATE MODULES
#
# mic = RespeakerMicrophoneModule('192.168.20.49:8000')
# asr = GoogleASRModule(rate=16000)

# mic = MicrophoneModule(rate=16000)
mic = RespeakerMicrophoneModule(respeaker)
asr = GoogleASRModule(rate=16000)
print("ASR")
# iasr = IncrementalizeASRModule()
dm = OpenDialModule(domain_dir=domain_dir, variables=opendial_variables)
print("OpenDial")
misty_camera = MistyCameraModule(misty_ip)
misty_refer = MistyReferModule(misty_ip)
misty_state = MistyStateModule(misty_ip)
print("Misty")
cropper = ImageCropperModule(top=200)
object_detector = Yolov8()
print("Yolo")
feature_extractor = ClipObjectFeatures(show=True)
print("CLIP")
wac = WordsAsClassifiersModule(wac_dir=wac_dir)
print("WAC")
debug = DebugModule()

print('All modules instantiated.')

# mic as input
mic.subscribe(asr)
asr.subscribe(wac)
wac.subscribe(dm)

# robot state as input
wac.subscribe(misty_refer)
misty_state.subscribe(misty_refer)
dm.subscribe(misty_refer)
misty_refer.subscribe(dm)
object_detector.subscribe(misty_refer)

# robot camera as input
misty_camera.subscribe(cropper)
cropper.subscribe(object_detector)
object_detector.subscribe(feature_extractor)
object_detector.subscribe(dm)
feature_extractor.subscribe(wac)

dm.subscribe(misty_refer)

# debug.subscribe(misty_refer)

print('All modules subscribed.')

#
# INITIALIZE MODULES
# 
mic.run()
asr.run()
# iasr.run()
dm.run()
object_detector.run()
feature_extractor.run()
# misty_state.run()
misty_refer.run()
misty_camera.run()
cropper.run()
wac.run()
# debug.run()
print('All modules running.')

input() # keep everything running

mic.stop()
asr.stop()
# iasr.stop()
dm.stop()
object_detector.stop()
feature_extractor.stop()
wac.stop()
misty_refer.stop()
misty_camera.stop()
cropper.stop()
# debug.stop()