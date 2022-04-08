from datetime import datetime
import os

import sqlalchemy as db
from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Boolean
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

FILE_PATH = os.path.abspath(os.path.join("data", "appdata.db"))

engine = db.create_engine(f"sqlite:///{FILE_PATH}")
Base = declarative_base()

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
    artist = Column(String)
    date_created = Column(DateTime)
    tracks = relationship(
        "Track", secondary=playlist_track, back_populates="playlists"
    )

    def __init__(self, title: str, artist: str, date_created: datetime):
        self.title = title
        self.artist = artist
        self.date_created = date_created

class Track(Base):
    __tablename__ = "track"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    path = Column(String)
    stream_id = Column(Integer, ForeignKey("stream.id"))
    stream = relationship("Stream", backref="track")
    playlists = relationship(
        "Playlist", secondary=playlist_track, back_populates="tracks"
    )
    
    def __init__(self, title: str, playlists: list[Playlist], path: str=None, stream_url: str=None):
        self.title = title
        self.playlists = playlists

        if path:
            self.path = path
        else:
            self.stream = Stream(stream_url)

class Stream(Base):
    __tablename__ = "stream"

    id = Column(Integer, primary_key=True)
    url = Column(String)

    def __init__(self, url: str):
        self.url = url

Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

post_playlist = Playlist("Post Playlist", "Post Malone", datetime.now())

circles = Track("Circles", [post_playlist], path="data\\tracks\\Post Malone - Circles.mp3")
rockstar = Track("Rockstar", [post_playlist], stream_url="https://www.youtube.com/watch?v=wEGOxgfdRVc")

post_playlist.tracks = [circles, rockstar]

# Playlist
session.add(post_playlist)

# Optional (tracks)
session.add(circles)
session.add(rockstar)

session.commit()
session.close()

playlists = session.query(Playlist).all()

for playlist in playlists:
    print(playlist.title)
    for i, track in enumerate(playlist.tracks):
        print(f"{i+1}. Track: {track.title}")
        print(f"{i+1}. Url/Path: {track.stream.url if track.stream else track.path}")
        print()
