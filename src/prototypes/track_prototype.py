from typing import Optional
from datetime import datetime
import os

from mutagen import File
from mutagen.mp3 import MP3

from stream import Stream

class Track:
    def __init__(self, title: str, album: str, local: bool, path: Optional[str]=None, stream: Optional[Stream]=None) -> None:
        self.title = title
        self.album = album
        self.path = path
        self.stream = stream

        self.date_added = datetime.fromtimestamp(os.path.getctime(self.path))

        mp3 = MP3(self.path)
        self.duration = int(mp3.info.length)
        self.sample_rate = mp3.info.sample_rate

        file = File(self.path, easy=True)

        try:
            self.artist = file["artist"][0]
        except Exception:
            self.artist = "Unknown Artist"

    def set_play_method(self, local: bool):
        self.local = local

    def play(self):
        if self.local:
            self.play_local()
        else:
            self.play_stream()

    def play_local(self):
        pass

    def play_stream(self):
        self.stream.play_default_stream()