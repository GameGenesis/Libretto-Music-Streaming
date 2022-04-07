import sqlalchemy as db

from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Boolean
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = db.create_engine('sqlite:///database.db')
Base = declarative_base()

playlist_track = Table(
    "playlist_track",
    Base.metadata,
    Column("playlist_id", Integer, ForeignKey("playlist.playlist_id")),
    Column("track_id", Integer, ForeignKey("track.track_id")),
)

class Playlist(Base):
    __tablename__ = "author"
    playlist_id = Column(Integer, primary_key=True)
    title = Column(String)
    artist = Column(String)
    date_created = Column(DateTime)
    tracks = relationship(
        "Track", secondary=playlist_track, back_populates="playlists"
    )

class Track(Base):
    __tablename__ = "track"
    track_id = Column(Integer, primary_key=True)
    title = Column(String)
    playlists = relationship(
        "Playlists", secondary=playlist_track, back_populates="tracks"
    )