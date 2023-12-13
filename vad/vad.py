import queue
from numpy import frombuffer, int16
import torch

import retico_core
from retico_core.audio import AudioIU



class VADModule(retico_core.AbstractModule):
    """A Voice Acticity Detection (VAD) module that consumes AudioIUs of arbitrary size and 
    outputs True or False whether a human is talking."""
    
    @staticmethod
    def name():
        return "VAD Module"

    @staticmethod
    def description():
        return "A consuming module that detects human voice."

    @staticmethod
    def input_ius():
        return [AudioIU]

    @staticmethod
    def output_iu():
        return None
    
    def __init__(self, confidence_threshold=.8, rate=16000,**kwargs):
        
        super().__init__(**kwargs)
        self.confidence_threshold = confidence_threshold
        self.rate = rate
        self.voiced_confidences = []
        self.client = None
        self.streaming_config = None
        self.num_samples = 1536
        self.audio_buffer = queue.Queue()

        self.latest_input_iu = None
        
            
    def process_update(self, update_message):
        for iu, ut in update_message:
            if ut != retico_core.UpdateType.ADD:
                continue
            self.audio_buffer.put(iu.raw_audio)
            if not self.latest_input_iu:
                self.latest_input_iu = iu
        return None


    # Taken from utils_vad.py
    def validate(model,
                inputs: torch.Tensor):
        with torch.no_grad():
            outs = model(inputs)
        return outs

    # Provided by Alexander Veysov
    def int2float(sound):
        abs_max = abs(sound).max()
        sound = sound.astype('float32')
        if abs_max > 0:
            sound *= 1/32768
        sound = sound.squeeze()  # depends on the use case
        return sound
    
    def setup(self):
        model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                              model='silero_vad',
                              force_reload=True)
        
        currently_talking = False
        self.model = model
        self.utils = utils

        (get_speech_timestamps,
         save_audio,
         read_audio,
         VADIterator,
         collect_chunks) = utils
        
    def produce_confidence(self, stream):
        # stream is the imput
        audio_chunk = stream.read(self.num_samples)
        audio_int16 = frombuffer(audio_chunk, int16)
        audio_float32 = self.int2float(audio_int16)
        
        # get the confidences and add them to the list to plot them later
        new_confidence = self.model(torch.from_numpy(audio_float32), self.rate).item()
        
        if(new_confidence > .8):
            self.currently_talking = True
            print('is talking')
        else:
            self.currently_talking = False
            print('is not talking')


    def shutdown(self):
        self.stream.close()