# Imports
import random
import time
from pygame import mixer
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

def get_playlists(parent_dir: str):
    playlists = [Playlist(os.path.join(parent_dir, current_dir), current_dir, "Artist", get_playlist_tracks(os.path.join(parent_dir, current_dir))) for current_dir in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, current_dir)) and is_compatible_dir(os.path.join(parent_dir, current_dir))]
    return playlists

def get_playlist_tracks(playlist_dir: str):
    return [Track(os.path.join(playlist_dir, f), f[:-4], playlist_dir) for f in os.listdir(playlist_dir) if os.path.isfile(os.path.join(playlist_dir, f)) and is_compatible_file(f)]

def init():
    global current_dir, playlists, playlist_index
    # Starting the mixer
    mixer.init()
    mixer.music.set_volume(volume)

def set_track_speed(multiplier: int=1):
    global track_index, current_pos
    mixer.init(frequency=int(playlists[playlist_index].tracks[track_index].sample_rate * multiplier))
    play_track(track_index, current_pos)

def play_track(track_index: int=0, start_time: int=0):
    global audio, length, playlists, playlist_index, current_pos, elapsed_time_change

    try:
        # Loading the track
        mixer.music.load(playlists[playlist_index].tracks[track_index].path)

        # Start playing the track
        mixer.music.play(start=start_time)

        # Queuing the next track
        mixer.music.queue(playlists[playlist_index].tracks[get_next_index(track_index, playlists[playlist_index].length)].path)
    except Exception:
        print("Can't play track! File format not supported!")

    length = playlists[playlist_index].tracks[track_index].duration

    current_pos = start_time
    elapsed_time_change = 0

def get_next_index(index, length):
    # Supports looping
    return 0 if index >= length - 1 else index + 1

def get_previous_index(index):
    return 0 if index <= 0 else index - 1

def next_playlist():
    global playlist_index, playlists, track_index
    track_index = 0
    playlist_index = get_next_index(playlist_index, len(playlists))
    play_track(track_index)

def previous_playlist():
    global playlist_index, track_index
    track_index = 0
    playlist_index = get_previous_index(playlist_index)
    play_track(track_index)

def next_track():
    global track_index
    track_index = get_next_index(track_index, playlists[playlist_index].length)
    play_track(track_index)

def previous_track():
    global track_index
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

def get_elapsed_time():
    global current_pos, elapsed_time_change
    return current_pos - elapsed_time_change + (mixer.music.get_pos() // 1000)

parent_dir = os.path.join("data", "playlists")
playlists = get_playlists(parent_dir)

playlist_index = 0
track_index = 0

current_pos = 0
elapsed_time_change = 0
SKIP_DURATION = 10

volume = 0.5
muted = False
MIN_VOLUME, MAX_VOLUME, VOLUME_INCREMENT = 0, 1, 0.1

speed = 1

init()
play_track(track_index)

while True:
    # Print instructions and get user input
    print('''Use '[' and ']' for cycling through playlists.
Use 'p' to pause, 'u' to unpause, 'r' to rewind, 'f' for forward, 'b' for back.
Use 'n' for next track, 'q' for previous track, 's' to shuffle tracks.
Use '+' to increase the volume, '-' to decrease the volume, and 'm' to mute/unmute.
Use 'e' to exit the program.''')
    muted_str = " (Muted)" if muted else ""
    print(f"[Volume: {int(volume*100)}%{muted_str}]")
    print(f"[Elapsed time: {time.strftime('%M:%S', time.gmtime(get_elapsed_time()))} of {time.strftime('%M:%S', time.gmtime(length))} ({time.strftime('%M:%S', time.gmtime(length-get_elapsed_time()))} remaining) || Title: {playlists[playlist_index].tracks[track_index].title} || Artist: {playlists[playlist_index].tracks[track_index].artist}]")
    playlists_list = [f"{i}: {e.get_info_string()}" for i, e in enumerate(playlists)]
    print(f"Playlists: {str(playlists_list)}. Current Playlist: {playlist_index}")
    query = input(">> ").lower()
    os.system("cls||clear")

    if "speed" in query:
        if ":" in query:
            speed = float(query.split(":")[1])
            set_track_speed(speed)
        else:
            print(f"Speed: x{speed}")
    elif query == ']':
        next_playlist()
    elif query == '[':
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
        mixer.music.rewind()
        current_pos = 0
        elapsed_time_change = mixer.music.get_pos() // 1000
    elif "time:" in query:
        current_pos = min(int(query.split(":")[1]), length)
        elapsed_time_change = mixer.music.get_pos() // 1000
        if current_pos >= length:
            next_track()
        mixer.music.pause()
        mixer.music.set_pos(current_pos)
        mixer.music.unpause()
    elif query == 'f':
        # Skipping 10s forward in a track
        current_pos = min(current_pos + (mixer.music.get_pos() // 1000) - elapsed_time_change + SKIP_DURATION, length)
        elapsed_time_change = mixer.music.get_pos() // 1000
        if current_pos >= length:
            next_track()
        mixer.music.pause()
        mixer.music.set_pos(current_pos)
        mixer.music.unpause()
    elif query == 'b':
        # Skipping 10s backward in a track
        current_pos = max(current_pos + (mixer.music.get_pos() // 1000) - elapsed_time_change - SKIP_DURATION, 0)
        elapsed_time_change = mixer.music.get_pos() // 1000
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
        mixer.music.set_volume(volume)
    elif query == '-':
        if muted:
            toggle_mute()
        volume = round(mixer.music.get_volume(), 1)
        volume = max(volume - VOLUME_INCREMENT, MIN_VOLUME)
        mixer.music.set_volume(volume)
    elif query == 'm':
        toggle_mute()
    elif query == 'e':
        # Stop the mixer
        mixer.music.stop()
        break