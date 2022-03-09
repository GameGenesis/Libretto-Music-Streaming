from pygame import mixer
from mutagen.mp3 import MP3
import os

def init():
    global tracks
    # Starting the mixer
    mixer.init()

    # Get playlist files
    dir = "temp"
    tracks = [os.path.join(dir, f) for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]

def play_track(track_index):
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
    print(length)

track_index = 0
current_pos = 0

init()
play_track(track_index)
