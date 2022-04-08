from datetime import datetime
import sqlalchemy as db

from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Boolean
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = db.create_engine('sqlite:///database.db')
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

class Track(Base):
    __tablename__ = "track"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    stream_id = Column(Integer, ForeignKey('stream.id'))
    stream = relationship("Stream", backref="track")
    playlists = relationship(
        "Playlist", secondary=playlist_track, back_populates="tracks"
    )

class Stream(Base):
    __tablename__ = 'stream'

    id = Column(Integer, primary_key=True)
    url = Column(String)

    def __init__(self, url: str):
        self.url = url

Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

post_playlist = Playlist(title="Post Playlist", artist="Post Malone", date_created=datetime.now())

circles = Track(title="Circles", stream=Stream("https://www.youtube.com/watch?v=wEGOxgfdRVc"), playlists=[post_playlist])
rockstar = Track(title="Rockstar", stream=Stream("https://www.youtube.com/watch?v=wEGOxgfdRVc"), playlists=[post_playlist])

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
        print(f"{i+1}. Url: {track.stream.url}")
        print()
