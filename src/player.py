import config
import time

from typing import Any, Optional

import lyricsgenius as lg
from youtubesearchpython import VideosSearch

from tkinter import Canvas, PhotoImage

from stream import Stream, StreamData
from database import Playlist, Track, playlist_manager


genius = None

gui_canvas = None
gui_elapsed_time_text = None
gui_track_slider = None
past_time = 0

gui_heart_button, gui_heart_empty_image, gui_heart_full_image = None, None, None
gui_loop_button, gui_no_loop_button_image, gui_loop_button_image = None, None, None
gui_play_button, gui_play_button_image, gui_pause_button_image = None, None, None
gui_track_title_text, gui_track_artist_text, gui_total_time_text = None, None, None

looping = False
playing = False
stream = None

def init(canvas: Canvas, elapsed_time_text: int, track_slider, heart_button: int, heart_empty_image: PhotoImage, heart_full_image: PhotoImage,
    loop_button: int, no_loop_button_image: PhotoImage, loop_button_image: PhotoImage,
    play_button: int, play_button_image: PhotoImage, pause_button_image: PhotoImage,
    track_title_text: int, track_artist_text: int, total_time_text: int):
    global genius
    global gui_canvas, gui_elapsed_time_text, gui_track_slider, gui_heart_button, gui_heart_empty_image, gui_heart_full_image
    global gui_loop_button, gui_no_loop_button_image, gui_loop_button_image
    global gui_play_button, gui_play_button_image, gui_pause_button_image
    global gui_track_title_text, gui_track_artist_text, gui_total_time_text

    genius = lg.Genius(config.GENIUS_ACCESS_TOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"], remove_section_headers=True, verbose=False)

    gui_canvas = canvas
    gui_elapsed_time_text = elapsed_time_text
    gui_track_slider = track_slider
    gui_heart_button = heart_button
    gui_heart_empty_image = heart_empty_image
    gui_heart_full_image = heart_full_image
    gui_loop_button = loop_button
    gui_no_loop_button_image = no_loop_button_image
    gui_loop_button_image = loop_button_image
    gui_play_button = play_button
    gui_play_button_image = play_button_image
    gui_pause_button_image = pause_button_image
    gui_track_title_text = track_title_text
    gui_track_artist_text = track_artist_text
    gui_total_time_text = total_time_text

def truncate_string(string: str, max_length: int, continuation_str: str="..") -> str:
    truncated_len = max_length-len(continuation_str)
    truncated_str = f"{string[:truncated_len]}{continuation_str}"
    return truncated_str if len(string) > max_length else string

def toggle_track_like(track: Track):
    global gui_canvas, gui_heart_button, gui_heart_empty_image, gui_heart_full_image

    liked_track = playlist_manager.track_is_liked(track)
    if liked_track:
        playlist_manager.remove_track_from_liked_songs(track)
    else:
        playlist_manager.add_track_to_liked_songs(track)

    liked_track = not liked_track
    gui_canvas.itemconfig(gui_heart_button, image=gui_heart_full_image if liked_track else gui_heart_empty_image)

def skip_backwards():
    if not stream:
        return

    stream.skip_backwards(10.0)

def skip_forwards():
    if not stream:
        return

    stream.skip_forwards(10.0)

def toggle_loop():
    global looping
    global gui_canvas, gui_loop_button, gui_no_loop_button_image, gui_loop_button_image
    if not stream:
        return

    looping = not looping
    stream.set_loop(looping)

    gui_canvas.itemconfig(gui_loop_button, image=gui_loop_button_image if looping else gui_no_loop_button_image)

def configure_play_state():
    global stream, playing
    global gui_canvas, gui_play_button, gui_play_button_image, gui_pause_button_image
    if playing:
        stream.unpause()
        gui_canvas.itemconfig(gui_play_button, image=gui_pause_button_image)
    else:
        stream.pause()
        gui_canvas.itemconfig(gui_play_button, image=gui_play_button_image)

def play_pause_track():
    global stream, playing
    global gui_canvas, gui_play_button, gui_play_button_image, gui_pause_button_image
    if not stream:
        return

    playing = not playing
    configure_play_state()

def update_elapsed_time(current_time, current_position):
    global gui_canvas, gui_elapsed_time_text, past_time

    gui_canvas.itemconfig(gui_elapsed_time_text, text=get_formatted_time(int(current_time)))

    if int(current_time) != past_time:
        gui_track_slider.set_position(current_position)

    past_time = int(current_time)

def play_database_track(track_id: int):
    track = playlist_manager.get_track(id=track_id)
    play_track(track.stream.url, track.title, track.artist, track.duration, track)

def play_search_track(track_title: str):
    global stream
    if stream:
        stream.stop()
    
    result = get_song_yt(track_title)
    play_track(result["link"], result["title"], result["channel"]["name"], get_unformatted_time(result["duration"]))

def play_track(stream_url: str, title: str, artist: str, duration: int, track: Optional[Track]=None):
    global stream, playing, gui_canvas
    if stream:
        stream.stop()

    if track:
        liked_track = playlist_manager.track_is_liked(track)
        gui_canvas.itemconfig(gui_heart_button, image=gui_heart_full_image if liked_track else gui_heart_empty_image)
        gui_canvas.tag_bind(gui_heart_button, "<ButtonPress-1>", lambda event, track=track: toggle_track_like(track))
    else:
        track_id = StreamData(stream_url).add_to_playlist()
        track = playlist_manager.get_track(id=track_id)
        liked_track = playlist_manager.track_is_liked(track)
        gui_canvas.itemconfig(gui_heart_button, image=gui_heart_full_image if liked_track else gui_heart_empty_image)
        gui_canvas.tag_bind(gui_heart_button, "<ButtonPress-1>", lambda event, track=track: toggle_track_like(track))

    title = truncate_string(title, 16)
    artist = truncate_string(artist, 16)

    gui_canvas.itemconfig(gui_track_title_text, text=title)
    gui_canvas.itemconfig(gui_track_artist_text, text=artist)

    track_duration = get_formatted_time(duration)
    gui_canvas.itemconfig(gui_total_time_text, text=track_duration)

    stream = Stream(stream_url, update_elapsed_time)
    stream.set_loop(looping)
    stream.play()

    playing = True
    configure_play_state()

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

def get_unformatted_time(time_str: str):
    h = 0
    if time_str.count(":") == 1:
        m, s = time_str.split(":")
    else:
        h, m, s = time_str.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)

def search(search_term: str):
    results = genius.search(search_term)
    return results

def get_song_yt(search_term: str) -> str | dict:
    videosSearch = VideosSearch(search_term, limit = 1)
    result = videosSearch.result()["result"][0]
    return result