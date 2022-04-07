from datetime import datetime

from old.track import Track

class Playlist:
    def __init__(self, title: str, artist: str, tracks: list[Track]) -> None:
        """
        Parameters
        ----------
        title : str
            The title of the playlist
        album : str
            The playlist artist
        tracks : list[Track]
            The list of tracks that are in the playlist
        """
        self.title = title
        self.artist = artist
        self.tracks = tracks

        self.date_created = datetime.now()

        self.length = len(self.tracks)
        self.total_duration = self.get_total_duration()

    def add_track(self, track: Track) -> None:
        """
        Appends a track to the playlist.
        Also updates the playlist track length and total playlist duration.

        Parameters
        ----------
        track : Track
            The track to append

        Raises
        ------
        NotImplementedError
            If no track is passed in as a parameter
        """
        if not Track:
            raise NotImplementedError

        self.tracks.append(track)
        self.length = len(self.tracks)
        self.total_duration += track.duration

    def get_total_duration(self) -> int:
        """
        Get the total duration of all the tracks in the playlist.

        Returns
        -------
        int
            the total duration duration of all the tracks in the playlist
        """
        return sum([t.duration for t in self.tracks])

    def __str__(self) -> str:
        """
        Returns a string that includes information about the object.

        Returns
        -------
        str
            information about the object
        """
        return f"Title: {self.title}, Artist: {self.artist}, Date Created: {self.date_created}, Total Duration: {self.total_duration}s"