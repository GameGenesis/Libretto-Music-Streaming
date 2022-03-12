import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials

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