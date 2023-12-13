README

@author Tyler Bowes
@date 4/28/2023

Creating a Voice Activity Detectiong module inside the audio.py library inside retico-core.  this file deals with audio-input, audio-output, and audio-consumption. So I decided to put this module into this audio.py library since VAD is an audio-consumption.

## Installation

download Retico-core and import module from audio.

## Usage

Utilize a audio input class and to produce results with the VAD class.  VAD class will take in audio and output true or false whether a human is speaking or not.  to print these result you will need to use the debug module and print the payload only.


## Contributing

I have seperated the audio.py file from retico-core for submittion.  Inside this file changes consist of two new imports and a new voice activity detection class.