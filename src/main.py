# Imports
import random
from pygame import mixer
from mutagen.mp3 import MP3
from datetime import datetime
import os

from playlist import Playlist
from track import Track

def is_compatible_file(file: str):
    extensions = [".mp3", ".wav", ".ogg"]
    # Return true if the file ends with any of the compatible file extensions
    return any([file.endswith(e) for e in extensions])

def is_compatible_dir(directory: str):
    # Return true if at least one of the files in the directory ends with any of the compatible file extensions
    return any([is_compatible_file(f) and os.path.isfile(os.path.join(directory, f)) for f in os.listdir(directory)])

def get_date_created(path: str):
    return datetime.fromtimestamp(os.path.getctime(path))

def get_playlists(parent_dir: str):
    playlists = [Playlist(os.path.join(parent_dir, current_dir), current_dir, "Artist", get_date_created(os.path.join(parent_dir, current_dir)), get_playlist_tracks(os.path.join(parent_dir, current_dir))) for current_dir in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, current_dir)) and is_compatible_dir(os.path.join(parent_dir, current_dir))]
    return playlists

def get_playlist_tracks(playlist_dir: str):
    return [os.path.join(playlist_dir, f) for f in os.listdir(playlist_dir) if os.path.isfile(os.path.join(playlist_dir, f)) and is_compatible_file(f)]

def init():
    global current_dir, playlists, playlist_index
    # Starting the mixer
    mixer.init()
    mixer.music.set_volume(volume)

def play_track(track_index: int=0):
    global audio, length, playlists, playlist_index

    # Loading the track
    mixer.music.load(playlists[playlist_index].tracks[track_index])
    audio = MP3(playlists[playlist_index].tracks[track_index])

    # Start playing the track
    mixer.music.play()

    # Getting the track length
    length = int(audio.info.length)
    
    mixer.music.queue(playlists[playlist_index].tracks[get_next_index(track_index, playlists[playlist_index].length)])

def get_next_index(index, length):
    # Supports looping
    return 0 if index >= length - 1 else index + 1

def get_previous_index(index):
    return 0 if index <= 0 else index - 1

def next_playlist():
    global current_pos, playlist_index, playlists, track_index
    current_pos = 0
    track_index = 0
    playlist_index = get_next_index(playlist_index, len(playlists))
    play_track(track_index)

def previous_playlist():
    global current_pos, playlist_index, track_index
    current_pos = 0
    track_index = 0
    playlist_index = get_previous_index(playlist_index)
    play_track(track_index)

def next_track():
    global current_pos, track_index
    current_pos = 0
    track_index = get_next_index(track_index, playlists[playlist_index].length)
    play_track(track_index)

def previous_track():
    global current_pos, track_index
    current_pos = 0
    track_index = get_previous_index(track_index)
    play_track(track_index)

def shuffle_track():
    # Plays a random track from the current playlist
    global current_pos, track_index
    track_index = random.randint(0, playlists[playlist_index].length - 1)
    play_track(track_index)

def toggle_mute():
    global volume, saved_volume, muted
    muted = not muted
    if muted:
        saved_volume = volume
        mixer.music.set_volume(MIN_VOLUME)
    else:
        mixer.music.set_volume(saved_volume)


parent_dir = os.path.join("data", "playlists")
playlists = get_playlists(parent_dir)

playlist_index = 0
track_index = 0

current_pos = 0
SKIP_DURATION = 10

volume = 0.5
muted = False
MIN_VOLUME, MAX_VOLUME, VOLUME_INCREMENT = 0, 1, 0.1

init()
play_track(track_index)

while True:
    # Print instructions and get user input
    print('''Use 'l' to list all playlists and '[' and ']' for cycling through playlists. 
Use 'p' to pause, 'u' to unpause, 'r' to rewind, 'f' for forward, 'b' for back. 
Use 'n' for next track, 'q' for previous track, 's' to shuffle tracks. 
Use '+' to increase the volume, '-' to decrease the volume, and 'm' to mute/unmute. 
Use 'e' to exit the program.''')
    muted_str = " (Muted)" if muted else ""
    print(f"[Volume: {int(volume*100)}%{muted_str}]")
    print(f"[Elapsed time (not including skips) - {(mixer.music.get_pos() // 1000)//60}:{(mixer.music.get_pos() // 1000)%60:02d} of {length//60}:{length%60:02d} || Path: {audio.filename}]")
    query = input(">> ")
    os.system("cls||clear")
    
    if query == 'l':
        playlists_list = [f"{i}: {e.get_info_string()}" for i, e in enumerate(playlists)]
        print(f"Playlists: {str(playlists_list)}. Current Playlist: {playlist_index}")
    if query == ']':
        next_playlist()
    if query == '[':
        previous_playlist()
    elif query == 'p':
        # Pausing the music
        print("[Paused]")
        mixer.music.pause()
    elif query == 'u':
        # Resuming the music
        mixer.music.unpause()
    elif query == 'r':
        # Rewinding the music
        current_pos = 0
        mixer.music.rewind()
    elif query == 'f':
        # Skipping 10s forward in a track
        current_pos = min(current_pos + (mixer.music.get_pos() // 1000) + SKIP_DURATION, length)
        if current_pos >= length:
            next_track()
        print(f"[{current_pos//60}:{current_pos%60:02d} of {length//60}:{length%60:02d} || Path: {audio.filename}]")
        mixer.music.pause()
        mixer.music.set_pos(current_pos)
        mixer.music.unpause()
    elif query == 'b':
        # Skipping 10s backward in a track
        current_pos = max(current_pos + (mixer.music.get_pos() // 1000) - SKIP_DURATION, 0)
        print(f"[{current_pos//60}:{current_pos%60:02d} of {length//60}:{length%60:02d} || Path: {audio.filename}]")
        mixer.music.pause()
        mixer.music.set_pos(current_pos)
        mixer.music.unpause()
    elif query == 'n':
        next_track()
    elif query == 'q':
        previous_track()
    elif query == 's':
        shuffle_track()
    elif query == '+':
        # Getting and setting the volume
        if muted:
            toggle_mute()
        volume = round(mixer.music.get_volume(), 1)
        volume = min(volume + VOLUME_INCREMENT, MAX_VOLUME)
        print(f"[Volume: {int(volume*100)}%]")
        mixer.music.set_volume(volume)
    elif query == '-':
        if muted:
            toggle_mute()
        volume = round(mixer.music.get_volume(), 1)
        volume = max(volume - VOLUME_INCREMENT, MIN_VOLUME)
        print(f"[Volume: {int(volume*100)}%]")
        mixer.music.set_volume(volume)
    elif query == 'm':
        toggle_mute()
        muted_str = " (Muted)" if muted else ""
        print(f"[Volume: {int(volume*100)}%{muted_str}]")
    elif query == 'e':
        # Stop the mixer
        mixer.music.stop()
        break