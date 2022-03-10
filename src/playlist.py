class Playlist:
    def __init__(self, path, title, artist, date_created, tracks):
        self.path = path
        self.title = title
        self.artist = artist
        self.date_created = date_created
        self.tracks = tracks

    def get_length(self):
        return len(self.tracks)

    def get_total_duration(self):
        return 0

    def get_info_string(self):
        return f"Title: {self.title}, Artist: {self.artist}, Date Created: {self.date_created}, Path: {self.path}"

    length = property(fget=get_length, doc="The number of tracks in the playlist.")
    total_duration = property(fget=get_total_duration, doc="The sum of the durations of all the tracks in the playlist.")