import os, sys

os.environ['GOOGLE_APPLICATION_CREDENTIALS']='/home/slimlab/retico_v2/creds.json'


prefix = '/home/slimlab/retico_v2/'
sys.path.append(prefix+'retico_respeakermic')
sys.path.append(prefix+'retico_core')
sys.path.append(prefix+'retico_googleasr')

from retico_core.debug import DebugModule
# from retico_core.audio import MicrophoneModule
from retico_googleasr.googleasr import GoogleASRModule
# from retico_core.text import IncrementalizeASRModule
from retico_respeakermic.respeaker import RespeakerMicrophoneModule

mic = RespeakerMicrophoneModule('192.168.0.152:8000')
# mic = MicrophoneModule(rate=16000)
# iasr = IncrementalizeASRModule()
debug = DebugModule()
asr = GoogleASRModule(rate=16000)

mic.subscribe(asr)
asr.subscribe(debug)
# iasr.subscribe(debug)

mic.run()
asr.run()
debug.run()

input()

asr.stop()
debug.stop()
debug.stop()