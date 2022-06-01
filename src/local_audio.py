from typing import Callable, Optional
from datetime import datetime
import os

import pygame
from pygame import mixer
from mutagen import File
from mutagen.mp3 import MP3

import player

class LocalAudio:
    MUSIC_END = pygame.USEREVENT+1
    muted = False

    def __init__(self, path: str, title: Optional[str]=None, volume: Optional[float]=1.0) -> None:
        """
        Parameters
        ----------
        path : str
            The local track file path
        title : str, optional
            The title of the track. If not specified, uses the file name from the track path
        volume : float, optional
            The default track volume (between MIN_VOLUME and MAX_VOLUME). If not set, it defaults to the max (1.0)
        """
        self.path = path
        if title:
            self.title = title
        else:
            title = os.path.basename(path)

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
    def get_next_index(index: int, length: int) -> int:
        """
        Gets the next index, then loops at the last index

        Parameters
        ----------
        index : int
            The current index
        length : int
            The length of a list

        Returns
        -------
        int
            The next index
        """
        return 0 if index >= length - 1 else index + 1

    @staticmethod
    def get_previous_index(index: int) -> int:
        """
        Gets the previous index, except when the index is 0, returns the same index

        Parameters
        ----------
        index : int
            The current index

        Returns
        -------
        int
            The previous index
        """
        return 0 if index <= 0 else index - 1

    @staticmethod
    def is_compatible_file(file_name: str) -> bool:
        """
        Checks if a file is compatible for local play

        Parameters
        ----------
        file_name : str
            The name of the file

        Returns
        -------
        bool
            Whether the file extension is compatible or not
        """
        extensions = [".mp3", ".wav", ".ogg"]
        # Return true if the file ends with any of the compatible file extensions
        return any([file_name.endswith(e) for e in extensions])

    @staticmethod
    def pause() -> None:
        """
        Pauses track playback

        Returns
        -------
        None
        """
        mixer.music.pause()

    @staticmethod
    def unpause() -> None:
        """
        Unpauses track playback

        Returns
        -------
        None
        """
        mixer.music.unpause()

    @staticmethod
    def stop() -> None:
        """
        Stops track playback

        Returns
        -------
        None
        """
        mixer.music.stop()

    @staticmethod
    def rewind(self) -> None:
        """
        Rewinds the current playing track

        Returns
        -------
        None
        """
        mixer.music.rewind()
        self.current_pos = 0
        self.elapsed_time_change = mixer.music.get_pos() // 1000

    @classmethod
    def get_volume(cls) -> tuple[float, bool]:
        """
        Returns a tuple containing the current volume (rounded to 2 decimal places) and whether the audio is muted or not

        Returns
        -------
        tuple
            the current volume (rounded to 2 decimal places) and whether the audio is muted or not
        """
        return round(mixer.music.get_volume(), 2), cls.muted

    @classmethod
    def set_volume(cls, volume: float) -> None:
        """
        Sets the volume of the audio player

        Parameters
        ----------
        volume : float
            The volume to set for the audio player (clamped between 0 and 1)

        Returns
        -------
        None
        """
        if volume <= 0:
            cls.muted = True
        elif cls.muted:
            cls.toggle_mute()
        volume = round(player.Utils.clamp01(volume), 2)
        mixer.music.set_volume(volume)

    @classmethod
    def toggle_mute(cls) -> bool:
        """
        Mutes or unmuted the music player

        Returns
        -------
        bool
            Whether the player is muted or unmuted
        """
        cls.muted = not cls.muted
        if cls.muted:
            saved_volume = cls.volume
            mixer.music.set_volume(cls.MIN_VOLUME)
        else:
            mixer.music.set_volume(saved_volume)
        return cls.muted

    def play(self, start_time: Optional[int]=0) -> None:
        """
        Plays the track from a path. Optionally, plays from a specified start time

        Parameters
        ----------
        start_time : int, optional
            The point in time (in seconds) of the song to start playback

        Returns
        -------
        None
        """
        try:
            # Loading the track
            mixer.music.load(self.path)

            # Start playing the track
            mixer.music.play(start=start_time)

            mixer.music.set_endevent(self.MUSIC_END)
        except Exception:
            print("Can't play track! File format not supported!")

    def on_end_callback(self, end_event: Optional[Callable]=None, *args, **kwargs) -> bool:
        """
        Calls an optional ends event callback when the current playing track ends.


        Parameters
        ----------
        end_event : Callable, optional
            The end event callback

        Returns
        -------
        bool
            Whether the current track is still playing
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == self.MUSIC_END:
                if end_event != None:
                    end_event(*args, **kwargs)
                return False
        return True

    def queue_track(self, track: "LocalAudio") -> bool:
        """
        Queues a new track to play when the current one ends


        Parameters
        ----------
        track : LocalAudio
            The next track to play

        Returns
        -------
        bool
            Whether the current track is still playing
        """
        return self.on_end_callback(end_event=lambda: track.play())


if __name__ == "__main__":
    tracks = [LocalAudio("data\\tracks\\Bazzi - Mine [Official Music Video].mp3"),
    LocalAudio("data\\tracks\\Post Malone - Circles.mp3")]
    index = 0
    while True:
        print(index)
        tracks[index].play()
        while tracks[index].on_end_callback():
            command = input()
            if command == "n":
                index = LocalAudio.get_next_index(index, len(tracks))
                break
            elif command == "b":
                index = LocalAudio.get_previous_index(index)
                break
        else:
            index += 1