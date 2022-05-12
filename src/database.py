from datetime import datetime
import os

import sqlalchemy as db
from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Boolean
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database file path
FILE_PATH = os.path.abspath(os.path.join("data", "appdata.db"))

# Creating the database engine and a base class for table creation
engine = db.create_engine(f"sqlite:///{FILE_PATH}")
Base = declarative_base()

# A table to store playlist-track relationships (many-to-many)
playlist_track = Table(
    "playlist_track",
    Base.metadata,
    Column("playlist_id", Integer, ForeignKey("playlist.id")),
    Column("track_id", Integer, ForeignKey("track.id")),
)

class Playlist(Base):
    __tablename__ = "playlist"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    date_created = Column(DateTime)
    downloaded = Column(Boolean)
    tracks = relationship(
        "Track", secondary=playlist_track, back_populates="playlists"
    )

    def __init__(self, title: str, date_created: datetime, downloaded: bool=False) -> None:
        """
        Parameters
        ----------
        title : str
            The title of the playlist
        date_created : datetime
            The date and time the playlist was created
        downloaded : bool
            Whether the contents of the playlist should be downloaded

        Returns
        -------
        None
        """
        self.title = title
        self.date_created = date_created
        self.downloaded = downloaded

    def get_length(self) -> int:
        """
        Returns the number of tracks in the playlist

        Returns
        -------
        int
            The number of tracks in the playlist
        """
        return len(self.tracks)

    def get_total_duration(self) -> int:
        """
        Get the total duration of all the tracks in the playlist.

        Returns
        -------
        int
            the total duration duration of all the tracks in the playlist
        """
        # return sum([t.duration for t in self.tracks])
        pass

class Track(Base):
    __tablename__ = "track"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    artist = Column(String)
    album = Column(String)
    duration = Column(Integer)
    path = Column(String)
    stream_id = Column(Integer, ForeignKey("stream.id"))
    stream = relationship("Stream", backref="track")
    liked = Column(Boolean)
    playlists = relationship(
        "Playlist", secondary=playlist_track, back_populates="tracks"
    )

    def __init__(self, title: str, artist: str, album: str, duration: int, playlists: list[Playlist], path: str=None, stream_url: str=None,
        liked: bool=False) -> None:
        self.title = title
        self.artist = artist
        self.album = album
        self.duration = duration
        self.playlists = playlists
        self.liked = liked

        if path:
            self.path = path
        else:
            self.stream = Stream(stream_url)

class Stream(Base):
    __tablename__ = "stream"

    id = Column(Integer, primary_key=True)
    url = Column(String)

    def __init__(self, url: str) -> None:
        self.url = url

class PlaylistManager:
    def __init__(self) -> None:
        Base.metadata.create_all(engine)
        Session = sessionmaker()
        Session.configure(bind=engine)
        self.session = Session()

    def get_or_create_playlist(self, title: str="New Playlist") -> Playlist:
        playlist = self.session.query(Playlist).filter_by(title=title).first()
        if playlist != None:
            return playlist

        playlist = Playlist(title=title, date_created=datetime.now())

        self.session.add(playlist)
        self.session.commit()
        return playlist

    def add_track_to_playlist(self, title: str, artist: str, album: str, duration: int, stream_url: str, playlist: Playlist) -> Track:
        track = self.session.query(Track).filter_by(title=title).first()
        if track == None:
            track = Track(title=title, artist=artist, album=album, duration=duration, playlists=[playlist], stream_url=stream_url)
            self.session.add(track)
        else:
            playlists = track.playlists
            if playlist not in playlists:
                playlists.append(playlist)
                track.playlists = playlists
        self.session.commit()
        return track

    def add_to_liked_songs(self, title: str, artist: str, album: str, duration: int, stream_url: str) -> None:
        liked_songs_playlist = self.get_or_create_playlist("Liked Songs")
        self.add_track_to_playlist(title, artist, album, duration, stream_url, liked_songs_playlist)

    def commit_session(self) -> None:
        self.session.commit()

    def close_session(self) -> None:
        self.session.close()

def test():
    playlist_manager = PlaylistManager()
    post_playlist = playlist_manager.get_or_create_playlist("Post Malone")

    playlist_manager.add_to_liked_songs("Rockstar", "Post Malone", "Hollywood's Bleeding", 221, "https://www.youtube.com/watch?v=UceaB4D0jpo")
    playlist_manager.add_to_liked_songs("Circles", "Post Malone", "Hollywood's Bleeding", 167, "https://www.youtube.com/watch?v=wXhTHyIgQ_U")
    playlist_manager.add_track_to_playlist("Circles", "Post Malone", "Hollywood's Bleeding", 167, "https://www.youtube.com/watch?v=wXhTHyIgQ_U", post_playlist)

    playlist_manager.close_session()

    playlists = playlist_manager.session.query(Playlist).all()

    for playlist in playlists:
        print(playlist.title)
        print(f"Number of Tracks: {playlist.get_length()}")
        for i, track in enumerate(playlist.tracks):
            print(f"{i+1}. Track: {track.title}")
            print(f"{i+1}. Url/Path: {track.stream.url if track.stream else track.path}")
            print()

if __name__ == "__main__":
    test()