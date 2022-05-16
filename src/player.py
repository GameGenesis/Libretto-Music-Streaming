import threading
import time
from typing import Any

from tkinter import Canvas, Event

from stream import Stream
from database import Playlist, Track

music_thread = None
stream = None

def truncate_string(string: str, max_length: int, continuation_str: str="..") -> str:
    truncated_len = max_length-len(continuation_str)
    truncated_str = f"{string[:truncated_len]}{continuation_str}"
    return truncated_str if len(string) > max_length else string

def play_track(event: Event, canvas: Canvas, track_title_text: int, title: str, track_artist_text: int, artist: str, url: str):
    global music_thread, stream
    if stream:
        stream.stop()
    if music_thread:
        music_thread.join()

    title = truncate_string(title, 16)
    canvas.itemconfig(track_title_text, text=title)
    canvas.itemconfig(track_artist_text, text=artist)
    stream = Stream(url)
    music_thread = threading.Thread(target=lambda: stream.play(False))
    # Make the thread terminate when the user exits the window
    music_thread.daemon = True
    music_thread.start()

def get_playlist_info(playlist: Playlist):
    total_duration = playlist.get_total_duration()
    hours = total_duration // 3600
    mins = (total_duration - (hours * 3600)) // 60
    secs = (total_duration - (hours * 3600) - (mins * 60))

    playlist_length = playlist.get_length()
    formatted_length = f"{playlist_length} songs" if playlist_length > 1 else f"{playlist_length} song"
    formatted_time = f"{hours} hr {mins} min" if hours > 0 else f"{mins} min {secs} sec"
    playlist_information = f"{formatted_length}, {formatted_time}"
    return playlist_information

def split_list(list: list[Any], size: int):
    """
    Splits a list into smaller-sized lists of a specified size
    """
    return (list[index:index+size] for index in range(0, len(list), size))

def get_track_duration(track: Track):
    track_duration = time.strftime('%#M:%S', time.gmtime(track.duration))
    return track_duration