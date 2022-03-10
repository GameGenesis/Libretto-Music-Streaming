class Playlist:
    def __init__(self, path, title, artist, date_created):
        self.path = path
        self.title = title
        self.artist = artist
        self.date_created = date_created

    def get_info_string(self):
        return f"Title: {self.title}, Artist: {self.artist}, Date Created: {self.date_created}, Path: {self.path}"