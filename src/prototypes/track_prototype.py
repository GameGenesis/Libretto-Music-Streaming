import inspect
import os
import sys

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from stream import Stream
from local_audio import LocalAudio
from audio import Audio

class Track:
    def __init__(self, album: str, audio: Audio | list[Audio], default_index: int=0) -> None:
        # self.title = audio.title
        self.album = album
        self.audio = audio
        self.default_index = default_index

    def play(self):
        if type(self.audio) == list:
            self.audio[self.default_index].play()
        else:
            self.audio.play()

track = Track("Album", Stream("https://www.youtube.com/watch?v=wEGOxgfdRVc"))
track.play()