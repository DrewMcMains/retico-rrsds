import functools
import threading
import time
import asyncio
import sys
from collections import deque
import random

# retico
import retico_core
from retico_core import abstract
from retico_opendialdm.dm import DialogueDecisionIU
from retico_core.dialogue import GenericDictIU
from retico_cozmorobot.cozmo_behaviors import CozmoBehaviors
from retico_vision.vision import DetectedObjectsIU
from retico_wacnlu.common import GroundedFrameIU

# cozmo
import sys
import os
sys.path.append(os.environ['COZMO'])
import cozmo
from cozmo.util import distance_mm, speed_mmps


class CozmoReferModule(retico_core.AbstractModule):

    @staticmethod
    def name():
        return "Cozmo Refer Module"

    @staticmethod
    def description():
        return "A Module that maps from DM decisions to Cozmo Robot actions in a reference task"

    @staticmethod
    def input_ius():
        return [DialogueDecisionIU,DetectedObjectsIU,GroundedFrameIU]

    @staticmethod
    def output_iu():
        return [GenericDictIU]

    def __init__(self, robot, use_viewer=False, force_viewer_on_top=False, **kwargs):
        super().__init__(**kwargs)
        self._use_viewer = use_viewer
        self._force_viewer_on_top = force_viewer_on_top
        self.robot = robot
        self._last_command = None
        self._input_iu = None
        self._current_word = None
        self.current_objects = None
        self.best_known_word = None
        self.cb = CozmoBehaviors(robot)
        self.queue = deque(maxlen=3)
        t = threading.Thread(target=self.run_dispatcher)
        t.start()

    def update_dialogue_state(self, signal, value):
        output_iu = GenericDictIU(creator=self, iuid=self.iu_counter)
        self.iu_counter+=1 # inherited
        output_iu.set_payload({signal:value})
        output_iu = abstract.UpdateMessage.from_iu(output_iu, abstract.UpdateType.ADD) 
        self.append(output_iu)

    def run_command(self, command, input_iu):
        if self.robot is None: return
        if command is None: return
        if self._last_command == command: return
        confidence = 0.0

        if '(' in command and ')' in command:
            word = command[command.find('(')+1:command.find(')')]
            self._current_word = word
            self.cb.say(word)
            command = command[:command.find('(')]

        if ':' in command:
            confidence = float(command[command.find(':')+1:])
            command = command[:command.find(':')]

        self._last_command = command
        self._input_iu = input_iu

        try:

            print('running command:', command)
            # self.cb.camera_on()
            # time.sleep(0.2)
            # self.cb.camera_off()
            # while self.robot.is_moving:
            #     self.robot.stop_all_motors()
            if 'begin_explore' == command:
                self.update_dialogue_state('exploring', True)
                self.cb.explore()
                pass
            if 'align_to_object' == command:
                for _ in range(3):
                    self.cb.turn_toward_top_object()
                self.update_dialogue_state('aligned', True)
            if 'approach_object' == command:
                self.cb.turn_toward_top_object()
                drive_dist = self.cb.go_to_top_object()
                if drive_dist < 5:
                    print('NEAR OBJECT')
                    self.update_dialogue_state('near_object', True)
            if 'check_confidence' == command:
                print(self._current_word, confidence)

                self.update_dialogue_state('aligned', False)
                self.update_dialogue_state('near_object', False)

                print(self._current_word, self.best_known_word)

                if self._current_word == self.best_known_word:
                    self.cb.say(self._current_word)
                    time.sleep(1.0)
                    self.cb.indicate_object()
                    self._last_command = None
                    self.update_dialogue_state('word_to_find', None)
                    self.update_dialogue_state('exploring', False)
                else:
                    self.cb.start_position()
                    w = random.choice(['hmmm', 'uhh', 'that'])
                    self.cb.say("{} not {}, that's {}".format(w, self._current_word, self.best_known_word))
                    self.cb.back_up()
                    self._last_command = 'begin_explore'
                    self.update_dialogue_state('begin_explore', True)

        except cozmo.exceptions.RobotBusy:
            print('robot is busy')
            

        # output_iu = self.create_iu(self._input_iu)
        # output_iu.set_payload({'':0})
        # self.append(output_iu)




    def run_dispatcher(self):

         while True:
            # print("checking queue", self.queue)
            if len(self.queue) == 0:
                # print("empty queue")
                time.sleep(3.0)
                # print("running last command")
                self.run_command(self._last_command, self._input_iu)
                # print("done running last command")
            else:
                print("extract from queue")
                input_iu = self.queue.popleft()
                decision = input_iu.payload['decision']
                concepts = input_iu.payload['concepts']
                print('new decision', decision)
                self.run_command(decision, input_iu)
                print("done running new decision")

    def process_update(self, update_message):
        for iu, ut in update_message:
            if ut != retico_core.UpdateType.ADD:
                continue
            if isinstance(iu, GroundedFrameIU):
                if 'best_known_word' in iu.payload:
                    self.best_known_word = iu.payload['best_known_word']
                if 'word_to_find' in iu.payload:
                    self._current_word = iu.payload['word_to_find']
                return None
                
            if isinstance(iu, DetectedObjectsIU):
                self.cb.set_current_objects(iu.payload)
                return None
            
            self.queue.clear() # drop frames, if still waiting
            self.queue.append(iu)

        return None
        
    # def process_iu(self, input_iu):

    #     if isinstance(input_iu, GroundedFrameIU):
    #         if 'best_known_word' in input_iu.payload:
    #             self.best_known_word = input_iu.payload['best_known_word']
    #         if 'word_to_find' in input_iu.payload:
    #             self._current_word = input_iu.payload['word_to_find']
    #         return None
            
    #     if isinstance(input_iu, DetectedObjectsIU):
    #         self.cb.set_current_objects(input_iu.payload)
    #         return None

    #     self.queue.clear() # drop frames, if still waiting
    #     self.queue.append(input_iu)

    #     return None


    def new_utterance(self):
        pass
        
    def setup(self):
        pass
        