# More info: https://spotipy.readthedocs.io/en/2.19.0/, https://developer.spotify.com/dashboard/login

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys

import config

spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=config.SPOTIPY_CLIENT_ID, client_secret=config.SPOTIPY_CLIENT_SECRET))

if len(sys.argv) > 1:
    name = ' '.join(sys.argv[1:])
else:
    name = 'Bazzi'

results = spotify.search(q='artist:' + name, type='artist')
items = results['artists']['items']
if len(items) > 0:
    artist = items[0]
    print(artist['name'], artist['images'][0]['url'])

# From the function, we can see that tracks tend to have features such as ‘danceability’, ‘energy’, ‘liveness’ etc
# track_features = spotify.audio_features()

# track_features = spotify.audio_analysis()
# track_features = spotify.track()