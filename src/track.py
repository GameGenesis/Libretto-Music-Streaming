from mutagen.mp3 import MP3
from datetime import datetime
import os

class Track:
    def __init__(self, path, title, artist, album):
        self.path = path
        self.title = title
        self.artist = artist
        self.album = album

    def get_date_added(self):
        return datetime.fromtimestamp(os.path.getctime(self.path))

    def get_duration(self):
        return int(MP3(self.path).info.length)

    date_created = property(fget=get_date_added, doc="The date the playlist was created.")
    duration = property(fget=get_duration, doc="The duration of the track.")