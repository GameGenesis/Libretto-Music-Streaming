from pygame import mixer
from mutagen.mp3 import MP3
import os

def is_compatible_file(file: str):
    extensions = [".mp3", ".wav", ".ogg"]
    # Return true if the file ends with any of the compatible file extensions
    return any([file.endswith(e) for e in extensions])

def init():
    global tracks
    # Starting the mixer
    mixer.init()

    # Get playlist files
    dir = "temp"
    tracks = [os.path.join(dir, f) for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) and is_compatible_file(f)]

def play_track(track_index: int=0):
    global audio, tracks, length

    # Loading the track
    mixer.music.load(tracks[track_index])
    audio = MP3(tracks[track_index])

    # Setting the volume
    mixer.music.set_volume(0.7)

    # Start playing the track
    mixer.music.play()

    # Getting the track length
    length = int(audio.info.length)

track_index = 0
current_pos = 0

init()
play_track(track_index)

while True:
    print("Press 'p' to pause, 'u' to unpause, 'r' to rewind, 'f' for forward, 'b' for back, 'n' for next track")
    print("Press 'e' to exit the program")
    query = input(">> ")
    
    if query == 'p':
        # Pausing the music
        mixer.music.pause()
    elif query == 'u':
        # Resuming the music
        mixer.music.unpause()
    elif query == 'r':
        # Rewinding the music
        current_pos = 0
        mixer.music.rewind()
    elif query == 'f':
        # Skipping 10 sec in a track
        current_pos = min(current_pos + (mixer.music.get_pos() // 1000) + 10, length)
        mixer.music.pause()
        mixer.music.set_pos(current_pos)
        mixer.music.unpause()
    elif query == 'b':
        # Reversing 10 sec in a track
        # TODO: Fix reverse bug
        current_pos = max(current_pos + (mixer.music.get_pos() // 1000) - 10, 0)
        mixer.music.pause()
        mixer.music.set_pos(current_pos)
        mixer.music.unpause()
    elif query == 'e':
        # Stop the mixer
        mixer.music.stop()
        break