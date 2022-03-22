# Imports
from typing import Callable, Optional
from datetime import datetime
import os

import pygame
from pygame import mixer
from mutagen import File
from mutagen.mp3 import MP3

class LocalAudio:
    MUSIC_END = pygame.USEREVENT+1
    muted = False
    MIN_VOLUME, MAX_VOLUME = 0, 1

    def __init__(self, path: str, title: str, album: str, volume: Optional[float]=1.0) -> None:
        self.path = path
        self.title = title
        self.album = album

        self.date_added = datetime.fromtimestamp(os.path.getctime(self.path))

        mp3 = MP3(self.path)
        self.duration = int(mp3.info.length)
        self.sample_rate = mp3.info.sample_rate

        file = File(self.path, easy=True)

        try:
            self.artist = file["artist"][0]
        except Exception:
            self.artist = "Unknown Artist"

        # Starting the mixer
        pygame.init()
        mixer.init()
        mixer.music.set_volume(volume)

        self.current_pos = 0

    @staticmethod
    def is_compatible_file(file: str):
        extensions = [".mp3", ".wav", ".ogg"]
        # Return true if the file ends with any of the compatible file extensions
        return any([file.endswith(e) for e in extensions])

    def play(self, start_time: Optional[int]=0):
        try:
            # Loading the track
            mixer.music.load(self.path)

            # Start playing the track
            mixer.music.play(start=start_time)

            mixer.music.set_endevent(self.MUSIC_END)
        except Exception:
            print("Can't play track! File format not supported!")

    def pause():
        mixer.music.pause()

    def unpause():
        mixer.music.unpause()

    def stop():
        mixer.music.stop()

    def rewind(self):
        mixer.music.rewind()
        self.current_pos = 0
        self.elapsed_time_change = mixer.music.get_pos() // 1000

    def toggle_mute(self):
        self.muted = not self.muted
        if self.muted:
            saved_volume = self.volume
            mixer.music.set_volume(self.MIN_VOLUME)
        else:
            mixer.music.set_volume(saved_volume)

    def on_end_callback(self, end_event: Optional[Callable]=None, *args, **kwargs):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == self.MUSIC_END:
                end_event(*args, **kwargs)
        return True
