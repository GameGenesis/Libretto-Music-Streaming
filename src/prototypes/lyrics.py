import lyricsgenius as lg

import config

genius = lg.Genius(config.GENIUS_ACCESS_TOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"], remove_section_headers=True)

song = genius.search_song(title="Circles", artist="Post Malone")
song.save_lyrics()
#from string import digits
print(song.lyrics[:-8]) #song.lyrics.replace("Embed", "").translate({ord(k): None for k in digits}) OR filter(lambda x: x.isalpha(), song.lyrics.replace("Embed", ""))

import json
with open('lyrics_postmalone_circles.json') as f:
    data = json.load(f)
print(data)

# When downloading a song (with search through Genius), also download the lyrics json with the album art

# Search for a song in the search bar; gives the top results with Genius (with a button to load more results, and specify number of results)
# Also gives results with YouTube search (for podcasts, etc.)
# When downloading, downloads and configures metadata and cover art and gets info from downloaded Genius json

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