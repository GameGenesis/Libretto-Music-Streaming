from datetime import datetime
import os

class Playlist:
    def __init__(self, path, title, artist, tracks):
        self.path = path
        self.title = title
        self.artist = artist
        self.tracks = tracks

    def get_date_created(self):
        return datetime.fromtimestamp(os.path.getctime(self.path))

    def get_length(self):
        return len(self.tracks)

    def get_total_duration(self):
        return 0

    def get_info_string(self):
        return f"Title: {self.title}, Artist: {self.artist}, Date Created: {self.date_created}, Path: {self.path}"

    date_created = property(fget=get_date_created, doc="The date the playlist was created.")
    length = property(fget=get_length, doc="The number of tracks in the playlist.")
    total_duration = property(fget=get_total_duration, doc="The sum of the durations of all the tracks in the playlist.")