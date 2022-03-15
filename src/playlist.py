from datetime import datetime
import os

class Playlist:
    def __init__(self, path, title, artist, tracks):
        self.path = path
        self.title = title
        self.artist = artist
        self.tracks = tracks

        self.date_created = datetime.fromtimestamp(int(os.path.getctime(self.path)))
        self.length = len(self.tracks)
        self.total_duration = self.get_total_duration()

    def add_track(self, track):
        self.tracks.append(track)
        self.length = len(self.tracks)
        self.total_duration = self.get_total_duration()

    def get_total_duration(self):
        return sum([t.duration for t in self.tracks])

    def get_info_string(self):
        return f"Title: {self.title}, Artist: {self.artist}, Date Created: {self.date_created}, Total Duration: {self.total_duration}s, Path: {self.path}"