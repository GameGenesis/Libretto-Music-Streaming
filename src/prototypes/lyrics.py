# More Info: https://lyricsgenius.readthedocs.io/en/master/, https://github.com/johnwmillr/LyricsGenius
# Search by title, artist, lyrics, genre
# Browse categories (genre)

import inspect
import os
import re
import sys
import lyricsgenius as lg

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import config

genius = lg.Genius(config.GENIUS_ACCESS_TOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"], remove_section_headers=True, verbose=False)

song = genius.search_song(title="Circles", artist="Post Malone")

print(song.artist, song.title, song.url, song.full_title, song.header_image_thumbnail_url, song.header_image_url, song.song_art_image_thumbnail_url, song.song_art_image_url, sep="\n")
# Replace html artifact in lyrics (Remove number followed by "Embed" if it comes right after any character that isn't a number)
print(re.sub(r"([^0-9])?\d+Embed", r"\1", song.lyrics))
# song.save_lyrics('lyrics.json')

print()

# Top 100 song results in the Pop genre
tag_results = list()
for i in range(5):
    for result in genius.tag("pop", page=i).get("hits"):
        tag_results.append(result)

for result in tag_results:
    print(result.get("title"))

print()

songs = genius.search("Post Malone")
print(songs)

# Search for a song in the search bar; gives the top results with Genius (with a button to load more results, and specify number of results)
# Also gives results with YouTube search (for podcasts, etc.)
# When downloading, downloads and configures metadata and cover art and gets info from Genius

#Searches all of "Pop Smoke"'s songs.
#artist = genius.search_artist("Pop Smoke")
#Searches 5 of "Pop Smoke"'s songs.
#artist = genius.search_artist("Pop Smoke",max_songs=5)
#Searches 5 of "Pop Smoke"'s songs via its Title.
#artist = genius.search_artist("Pop Smoke",max_songs=5,sort="title")
# Sorts = popularity release_date title
#song = artist.song("Dior")

# songs = artist.songs
# print(songs)