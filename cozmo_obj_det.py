import threading
import time

# set vars before importing modules
import os
import sys

os.environ['GOOGLE_APPLICATION_CREDENTIALS']='/home/slimlab/retico_v2/creds.json'
os.environ['PYOD'] = '/home/slimlab/retico_v2/pyopendial'
os.environ['COZMO'] = "/home/casey/git/cozmo-python-sdk/src"

prefix = '/home/slimlab/retico_v2/'
sys.path.append(prefix+'retico_core')
sys.path.append(prefix+'retico_opendialdm')
sys.path.append(prefix+'retico_wacnlu')
sys.path.append(prefix+'retico_cozmorobot')
sys.path.append(prefix+'retico_clip')
sys.path.append(prefix+'retico_vision')
sys.path.append(prefix+'retico_yolov8')
sys.path.append(prefix+'retico_whisperasr')
sys.path.append(prefix+'retico_respeakermic')
sys.path.append(prefix+'retico_googleasr')

sys.path.append(os.environ['COZMO'])
import cozmo

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
from retico_cozmorobot.cozmo_camera import CozmoCameraModule
from retico_cozmorobot.cozmo_refer import CozmoReferModule
from retico_cozmorobot.cozmo_state import CozmoStateModule
from retico_clip.clip import ClipObjectFeatures
from retico_yolov8.yolov8 import Yolov8
from retico_respeakermic.respeaker import RespeakerMicrophoneModule
# show_audio_devices()

respeaker = '192.168.0.152:8000'
mic = RespeakerMicrophoneModule(respeaker)

def init_all(robot : cozmo.robot.Robot):

    domain_dir = '/home/slimlab/retico_v2/data/cozmo/dm/dialogue.xml'
    wac_dir = '/home/slimlab/retico_v2/data/wac'

    opendial_variables = ['face_count', # CozmoStateModule
                           'num_objs', # ObjectDetector
                           'near_object', # CozmoRefer
                           'exploring', # CozmoRefer
                           'aligned', # CozmoRefer
                           'word_to_find', # WordsAsClassifiersModule
                           'best_object', # WordsAsClassifiersModule
                           'obj_confidence'] # WordsAsClassifiersModule

    #
    # INSTANTIATE MODULES
    #
    # mic = RespeakerMicrophoneModule('192.168.20.49:8000')
    # asr = GoogleASRModule(rate=16000)

    # mic = MicrophoneModule(rate=16000)
    asr = GoogleASRModule(rate=16000)
    print("ASR")
    # iasr = IncrementalizeASRModule()
    dm = OpenDialModule(domain_dir=domain_dir, variables=opendial_variables)
    print("OpenDial")
    # cozmo_camera = WebcamModule()
    cozmo_camera = CozmoCameraModule(robot)
    cozmo_refer = CozmoReferModule(robot)
    cozmo_state = CozmoStateModule(robot)
    print("Cozmo")
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
    # mic.subscribe(debug)
    # asr.subscribe(iasr)
    asr.subscribe(wac)
    # dm.subscribe(debug)
    wac.subscribe(dm)

    # robot state as input
    # cozmo_state.subscribe(dm)
    # wac.subscribe(cozmo_refer)

    # robot camera as input
    cozmo_camera.subscribe(object_detector)
    object_detector.subscribe(feature_extractor)
    object_detector.subscribe(dm)
    feature_extractor.subscribe(wac)

    dm.subscribe(cozmo_refer)
    wac.subscribe(cozmo_refer)
    object_detector.subscribe(cozmo_refer)
    cozmo_refer.subscribe(dm)

    # debug.subscribe(cozmo_refer)

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
    cozmo_camera.run()
    # cozmo_state.run()
    cozmo_refer.run()
    wac.run()
    debug.run()
    print('All modules running.')

    input() # keep everything running

    mic.stop()
    asr.stop()
    # iasr.stop()
    dm.stop()
    object_detector.stop()
    feature_extractor.stop()
    wac.stop()
    # cozmo_refer.stop()
    cozmo_camera.stop()

cozmo.run_program(init_all, use_viewer=True, force_viewer_on_top=False )