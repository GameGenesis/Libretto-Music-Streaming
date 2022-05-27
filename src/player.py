from unittest import result
import config
import threading
import time
import re

from typing import Any

import lyricsgenius as lg

from tkinter import Canvas, PhotoImage

from stream import Stream
from database import Playlist, Track, playlist_manager


genius = None
search_thread = None

gui_canvas = None
gui_elapsed_time_text = None
gui_track_slider = None
past_time = 0

looping = False
playing = False
music_thread = None
stream = None

def init(canvas: Canvas, elapsed_time_text: int, track_slider):
    global genius, gui_canvas, gui_elapsed_time_text, gui_track_slider

    genius = lg.Genius(config.GENIUS_ACCESS_TOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"], remove_section_headers=True, verbose=False)

    gui_canvas = canvas
    gui_elapsed_time_text = elapsed_time_text
    gui_track_slider = track_slider

def truncate_string(string: str, max_length: int, continuation_str: str="..") -> str:
    truncated_len = max_length-len(continuation_str)
    truncated_str = f"{string[:truncated_len]}{continuation_str}"
    return truncated_str if len(string) > max_length else string

def toggle_track_like(track: Track, canvas: Canvas,
    heart_button: int, heart_empty_image: PhotoImage, heart_full_image: PhotoImage):
    liked_track = playlist_manager.track_is_liked(track)
    if liked_track:
        playlist_manager.remove_track_from_liked_songs(track)
    else:
        playlist_manager.add_track_to_liked_songs(track)

    liked_track = not liked_track
    canvas.itemconfig(heart_button, image=heart_full_image if liked_track else heart_empty_image)

def skip_backwards():
    if not stream:
        return

    stream.skip_backwards(10.0)

def skip_forwards():
    if not stream:
        return

    stream.skip_forwards(10.0)

def toggle_loop(canvas: Canvas, loop_button: int, no_loop_button_image: PhotoImage, loop_button_image: PhotoImage):
    global looping
    if not stream:
        return

    looping = not looping
    stream.set_loop(looping)

    canvas.itemconfig(loop_button, image=loop_button_image if looping else no_loop_button_image)

def configure_play_state(canvas: Canvas, play_button: int, play_button_image: PhotoImage, pause_button_image: PhotoImage):
    global stream, playing
    if playing:
        stream.unpause()
        canvas.itemconfig(play_button, image=pause_button_image)
    else:
        stream.pause()
        canvas.itemconfig(play_button, image=play_button_image)

def play_pause_track(canvas: Canvas, play_button: int, play_button_image: PhotoImage, pause_button_image: PhotoImage):
    global stream, playing
    if not stream:
        return

    playing = not playing
    configure_play_state(canvas, play_button, play_button_image, pause_button_image)

def update_elapsed_time(current_time, current_position):
    global gui_canvas, gui_elapsed_time_text, past_time

    gui_canvas.itemconfig(gui_elapsed_time_text, text=get_formatted_time(int(current_time)))

    if int(current_time) != past_time:
        gui_track_slider.set_position(current_position)
    
    past_time = int(current_time)

def play_new_track(canvas: Canvas, track_id: int, track_title_text: int, track_artist_text: int,
    heart_button: int, heart_empty_image: PhotoImage, heart_full_image: PhotoImage,
    play_button: int, play_button_image: PhotoImage, pause_button_image: PhotoImage,
    total_time_text: int):
    global music_thread, stream, playing
    if stream:
        stream.stop()
    if music_thread:
        music_thread.join()

    track = playlist_manager.get_track(id=track_id)

    title = truncate_string(track.title, 16)
    artist = truncate_string(track.artist, 16)

    canvas.itemconfig(track_title_text, text=title)
    canvas.itemconfig(track_artist_text, text=artist)

    liked_track = playlist_manager.track_is_liked(track)
    canvas.itemconfig(heart_button, image=heart_full_image if liked_track else heart_empty_image)
    canvas.tag_bind(heart_button, "<ButtonPress-1>", lambda event, track=track, canvas=canvas:
        toggle_track_like(track, canvas, heart_button, heart_empty_image, heart_full_image))

    track_duration = get_formatted_time(track.duration)
    canvas.itemconfig(total_time_text, text=track_duration)

    stream = Stream(track.stream.url, update_elapsed_time)
    music_thread = threading.Thread(target=lambda: stream.play())
    # Make the thread terminate when the user exits the window
    music_thread.daemon = True
    music_thread.start()

    playing = True
    configure_play_state(canvas, play_button, play_button_image, pause_button_image)

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

def get_formatted_time(seconds: int):
    return time.strftime('%#M:%S', time.gmtime(seconds))

def search(search_term: str):
    global search_thread
    if search_thread:
        search_thread.join()

    # search_thread = threading.Thread(target=lambda: search_multithreaded(search_term))
    # # Make the thread terminate when the user exits the window
    # search_thread.daemon = True
    # search_thread.start()

    from multiprocessing.pool import ThreadPool
    pool = ThreadPool(processes=1)

    async_result = pool.apply_async(search_multithreaded, args=(search_term,))
    results = async_result.get()
    return results

def search_multithreaded(search_term: str):
    results = genius.search(search_term)
    # print(results)
    return results