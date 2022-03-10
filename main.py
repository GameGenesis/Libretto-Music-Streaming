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
    mixer.music.set_volume(volume)

    # Get playlist files
    dir = "temp"
    tracks = [os.path.join(dir, f) for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) and is_compatible_file(f)]

def play_track(track_index: int=0):
    global audio, tracks, length

    # Loading the track
    mixer.music.load(tracks[track_index])
    audio = MP3(tracks[track_index])


    # Start playing the track
    mixer.music.play()

    # Getting the track length
    length = int(audio.info.length)
    
    mixer.music.queue(tracks[get_next_track_index(track_index, len(tracks) - 1)])

def get_next_track_index(index, length):
    return 0 if track_index >= length else index + 1

def next_track():
    global current_pos, track_index, tracks
    current_pos = 0
    track_index = get_next_track_index(track_index, len(tracks) - 1)
    play_track(track_index)

track_index = 0
current_pos = 0
volume = 0.5
MIN_VOLUME, MAX_VOLUME = 0, 1

init()
play_track(track_index)

while True:
    print("Press 'p' to pause, 'u' to unpause, 'r' to rewind, 'f' for forward, 'b' for back, 'n' for next track")
    print("Press '+' to increase the volume and '-' to decrease the volume")
    print("Press 'e' to exit the program")
    query = input(">> ")
    os.system("cls||clear")
    
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
        if current_pos >= length:
            next_track()
        print(f"[{current_pos//60}:{current_pos%60:02d} of {length//60}:{length%60:02d} || Path: {audio.filename}]")
        mixer.music.pause()
        mixer.music.set_pos(current_pos)
        mixer.music.unpause()
    elif query == 'b':
        # Reversing 10 sec in a track
        current_pos = max(current_pos + (mixer.music.get_pos() // 1000) - 10, 0)
        print(f"[{current_pos//60}:{current_pos%60:02d} of {length//60}:{length%60:02d} || Path: {audio.filename}]")
        mixer.music.pause()
        mixer.music.set_pos(current_pos)
        mixer.music.unpause()
    elif query == 'n':
        next_track()
    elif query == '+':
        # Getting and setting the volume
        volume = round(mixer.music.get_volume(), 1)
        volume = min(volume + 0.1, MAX_VOLUME)
        print(f"[Volume: {int(volume*100)}%]")
        mixer.music.set_volume(volume)
    elif query == '-':
        volume = round(mixer.music.get_volume(), 1)
        volume = max(volume - 0.1, MIN_VOLUME)
        print(f"[Volume: {int(volume*100)}%]")
        mixer.music.set_volume(volume)
    elif query == 'e':
        # Stop the mixer
        mixer.music.stop()
        break