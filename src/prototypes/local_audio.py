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
    MIN_VOLUME, MAX_VOLUME = 0.0, 1.0

    def __init__(self, path: str, title: str, album: str, volume: Optional[float]=1.0) -> None:
        """
        Parameters
        ----------
        path : str
            The local track file path
        title : str
            The title of the track
        album : str
            The album of the track
        volume : float, optional
            The default track volume (between MIN_VOLUME and MAX_VOLUME). If not set, it defaults to the max (1.0)
        """
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
    def get_next_index(index, length):
        # Supports looping
        return 0 if index >= length - 1 else index + 1

    @staticmethod
    def get_previous_index(index):
        return 0 if index <= 0 else index - 1

    @staticmethod
    def is_compatible_file(file: str):
        extensions = [".mp3", ".wav", ".ogg"]
        # Return true if the file ends with any of the compatible file extensions
        return any([file.endswith(e) for e in extensions])

    @staticmethod
    def pause():
        mixer.music.pause()

    @staticmethod
    def unpause():
        mixer.music.unpause()

    @staticmethod
    def stop():
        mixer.music.stop()

    @staticmethod
    def rewind(self):
        mixer.music.rewind()
        self.current_pos = 0
        self.elapsed_time_change = mixer.music.get_pos() // 1000

    @classmethod
    def get_volume(cls) -> tuple[float, bool]:
        return round(mixer.music.get_volume(), 2), cls.muted

    @classmethod
    def set_volume(cls, volume: float):
        if volume <= 0:
            cls.muted = True
        elif cls.muted:
            cls.toggle_mute()
        volume = round(max(min(volume, cls.MAX_VOLUME), cls.MIN_VOLUME), 2)
        mixer.music.set_volume(volume)

    @classmethod
    def toggle_mute(cls):
        cls.muted = not cls.muted
        if cls.muted:
            saved_volume = cls.volume
            mixer.music.set_volume(cls.MIN_VOLUME)
        else:
            mixer.music.set_volume(saved_volume)

    def play(self, start_time: Optional[int]=0):
        try:
            # Loading the track
            mixer.music.load(self.path)

            # Start playing the track
            mixer.music.play(start=start_time)

            mixer.music.set_endevent(self.MUSIC_END)
        except Exception:
            print("Can't play track! File format not supported!")

    def on_end_callback(self, end_event: Optional[Callable]=None, *args, **kwargs):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == self.MUSIC_END:
                end_event(*args, **kwargs)
        return True
    
    def queue_track(self, track):
        return self.on_end_callback(end_event=lambda: track.play())


if __name__ == "__main__":
    tracks = [LocalAudio("data\playlists\Bazzi\Bazzi - Mine [Official Music Video].mp3", "Mine", "Album"),
    LocalAudio("data\playlists\Post Malone\Post Malone - Circles.mp3", "Circles", "Album")]
    for index, track in enumerate(tracks):
        track.play()
        second_track = tracks[LocalAudio.get_next_index(index, len(tracks))]
        while track.queue_track(second_track):
            pass