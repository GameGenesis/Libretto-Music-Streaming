import re
import urllib.request
import vlc
import time

class RadioStation:
    def __init__(self, url: str):
        self.url = url
        # Get radio streams from url
        self.streams = self.get_streams()
        self.set_default_stream()
    
    def set_default_stream(self, stream_index: int=0):
        # Set the stream that will be played by default
        if stream_index < len(self.streams):
            self.default_stream = self.streams[stream_index]

    def get_streams(self):
        request = urllib.request.Request(self.url)
        response = urllib.request.urlopen(request)
        raw_file = response.read().decode("utf-8")
        
        # Return the stream urls with regular expressions
        return re.findall(r"stream\":\"(.*?)\"", raw_file)

'''
Finding the stream URL using Chrome Dev Tools or Mozilla Firefox Firebug:
- Right click
- View page source
- Find stream urls
'''

'''
99.9 Virgin Radio
"hls_stream":"http://playerservices.streamtheworld.com/api/livestream-redirect/CKFMFM_ADP.m3u8"
"secure_mp3_pls_stream":"https://playerservices.streamtheworld.com/pls/CKFMFM.pls"
"pls_stream":"http://playerservices.streamtheworld.com/pls/CKFMFMAAC.pls"
"secure_hls_stream":"https://playerservices.streamtheworld.com/api/livestream-redirect/CKFMFM_ADP.m3u8"
"secure_pls_stream":"https://playerservices.streamtheworld.com/pls/CKFMFMAAC.pls"

Belgian radio station (MNM) example: http://icecast.vrtcdn.be/mnm-high.mp3 (includes now playing info)

IHeart radio playlist: https://playerservices.streamtheworld.com/pls/ST13_S01.pls
'''