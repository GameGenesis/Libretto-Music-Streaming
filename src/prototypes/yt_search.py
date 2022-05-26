import inspect
import os
import sys
from youtubesearchpython import VideosSearch

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from stream import StreamData

videosSearch = VideosSearch('Lea Makhoul Ratata', limit = 1)
results = videosSearch.result()["result"]

for result in results:
    print(result["link"])
    print(result["title"])
    print(result["channel"]["name"])
    print(result["duration"])
    print(result["publishedTime"])
    print(result["thumbnails"][0]["url"])
    print(result["thumbnails"][1]["url"])
    print()
    stream_data = StreamData(result["link"])
    print(stream_data.title, stream_data.artist, stream_data.album, stream_data.duration)