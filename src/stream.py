import os
import re
import urllib.request
import time
from pathlib import Path

import vlc
import requests
from bs4 import BeautifulSoup

from pytube import YouTube
from moviepy.editor import AudioFileClip
import mutagen

class Stream:
    '''Supports radio streaming, podcast streaming, and YouTube audio streams. Also supports downloading streams.'''

    def __init__(self, url: str, streams_override: list[str]=None, title_override:str=None) -> None:
        self.streams = []
        if not streams_override:
            self.url = url
            # Get streams from url and if available, the pafy youtube stream
            self.streams, self.youtube_streams = Stream.get_streams(url)
            self.set_default_stream()

            if not self.youtube_streams:
                # Get website title
                soup = BeautifulSoup(urllib.request.urlopen(url), features="html.parser")
                # Get stream title and remove white spaces and special/escape characters
                self.title = soup.title.text.replace("|", "").split()
                self.title = " ".join(self.title)
            else:
                yt = YouTube(self.url)
                self.title = yt.title
                self.artist = yt.author
                self.duration = yt.length
        else:
            # Assign streams if streams are valid
            if Stream.check_stream_validity(streams_override[0])[0]:
                self.streams = streams_override
            self.set_default_stream()

            try:
                # Try getting a website url from the default stream
                url = requests.get(self.default_stream, stream=True).headers.get("icy-url")
                # Get website title
                soup = BeautifulSoup(urllib.request.urlopen(url), features="html.parser")
                # Get stream title and remove white spaces and special/escape characters
                self.title = " ".join(soup.title.text.split())
            except:
                if not title_override:
                    self.title = "New Radio Station"

    @staticmethod
    def is_stream_playlist(stream_url: str) -> bool:
        # Create a list of playlist url extensions
        playlist_exts = ["pls", "m3u", "xspf"]
        # Get the first 4 characters of a url extension
        ext = stream_url.rpartition(".")[-1][:4]
        # Remove trailing characters that aren't part of the extension
        for char in "/?&#":
            ext = ext.replace(char, "")
        # Determine if the stream is a playlist
        return ext in playlist_exts

    @staticmethod
    def check_stream_validity(stream_url: str) -> tuple[bool, vlc.State]:
        try:
            # Try opening the stream url
            urllib.request.urlopen(stream_url)
        except urllib.error.HTTPError as e:
            # Return the HTTP status code error that was sent with the response (e.g. 404, 501, ...)
            print(f"HTTP Error: {e.code}")
        except urllib.error.URLError as e:
            # Not an HTTP-specific error (e.g. connection refused)
            print(f"URL Error: {e.reason}")
        except Exception as e:
            # Not an HTTP-specific or URL error (e.g. unknow url type)
            print(f"Error: {e}")
        else:
            # Start a vlc instance and try playing the stream
            instance = vlc.Instance()
            player = instance.media_player_new()
            player.audio_set_mute(True)

            is_playlist = Stream.is_stream_playlist(stream_url)
            if is_playlist:
                player = instance.media_list_player_new()
                media = instance.media_list_new([stream_url])
                player.set_media_list(media)
            else:
                media = instance.media_new(stream_url)
                player.set_media(media)

            player.play()

            print("Checking the stream validity...")
            time.sleep(2)
            # Get the player state
            state = player.get_state()
            # Return true if the state is not an error
            if state != vlc.State.Error and state != vlc.State.Ended:
                player.stop()
                print("Stream is valid!")
                return True, state
            print(f"Stream is not valid! Player State: {state}")
            return False, state
        print("Stream is not valid!")
        return False, None

    @staticmethod
    def is_supported_stream(stream: str, supported_extensions: list[str]) -> bool:
        return any(extension in stream for extension in supported_extensions)

    @staticmethod
    def get_streams(url: str) -> list[str]:
        # Inititalize empty streams list
        streams = []
        youtube_streams = None
        youtube_regex = "^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
        if re.search(youtube_regex, url):
            streams, youtube_streams = Stream.get_youtube_audio_streams(url)
            return streams, youtube_streams

        # Try opening the url
        request = urllib.request.Request(url)
        try:
            response = urllib.request.urlopen(request)
        except Exception as e:
            print(f"Could not open the specified URL. Error: {e}")
            return streams, youtube_streams

        # Decoding the page source
        raw_file = response.read().decode("utf-8")

        regex_terms = ["stream", "file", "@id", "fileURL", "streamURL", "mediaURL", "associatedMedia"]
        # Return the stream urls that match the regular expressions
        for term in regex_terms:
            if streams:
                return streams, youtube_streams
            streams = re.findall(f"{term}\":\"(.*?)\"", raw_file)

        # Search terms for Apple Podcasts, Google Podcasts, etc.
        specialized_regex_terms = [r"assetUrl\\\":\\\"(.*?)\"" , r"jsdata=\"Kwyn5e;(.*?);", r"url\":\"(.*?)\"", r"src=\"(.*?)\"", r"href=\"(.*?)\""]
        for term in specialized_regex_terms:
            if streams:
                return streams, youtube_streams
            streams = re.findall(term, raw_file)
            # Remove all results without the "mp3" extension (Due to these regular expressions being very generalized)
            for stream in streams:
                if ".mp3" not in stream:
                    streams.remove(stream)
        return streams, youtube_streams

    @staticmethod
    def get_youtube_audio_streams(url: str):
        yt = YouTube(url)
        youtube_streams = yt.streams.filter(only_audio=True).order_by("bitrate").desc()
        streams = [stream.url for stream in youtube_streams]
        # stream_abrs = [stream.abr for stream in youtube_streams] # (Debug)
        return streams, youtube_streams

    def set_default_stream(self, stream_index: int=0):
        # Set the stream that will be played by default
        if stream_index < len(self.streams):
            self.default_stream = self.streams[stream_index]
            # Determine if the default stream is a playlist
            self.is_playlist = Stream.is_stream_playlist(self.default_stream)
        else:
            self.default_stream = None
            print("Stream index is out of range!")

    def add_stream_manual(self, stream_url: str, default: bool=True) -> int:
        # Return -1 if the stream could not be added
        index = -1

        # Get the stream validity before trying to add the stream
        valid_stream = self.check_stream_validity(stream_url)[0]
        if not valid_stream:
            print("Could not add stream!")
            return index

        if default:
            # Add as the first stream in the list
            index = 0
            self.streams.insert(index, stream_url)
            self.set_default_stream()
        else:
            # Add as the last stream in the list
            self.streams.append(stream_url)
            index = len(self.streams) - 1

        # Return the added stream index
        return index

    def play_default_stream(self):
        # Return if there is no default stream
        if not self.default_stream:
            print("Can't play radio stream; there is no default stream!")
            return

        # Create a vlc instance and player
        self.vlc_instace = vlc.Instance()
        self.player = self.vlc_instace.media_player_new()
        self.player.audio_set_mute(False)

        if self.is_playlist:
            # Set the default stream playlist as the playable media list
            self.player = self.vlc_instace.media_list_player_new()
            self.media = self.vlc_instace.media_list_new([self.default_stream])
            self.player.set_media_list(self.media)
        else:
            # Set the default stream as the playable media
            self.media = self.vlc_instace.media_new(self.default_stream)
            self.player.set_media(self.media)

        self.player.play()

        # Record the previously playing track
        previously_playing = None

        # While the stream is still playing
        while self.player.is_playing:
            time.sleep(1)

            # Debug information
            if not self.is_playlist:
                print(f"Percent: {round(self.player.get_position() * 100, 2)}%") #set_position
                self.current_time = self.player.get_time() // 1000 # self.player.set_time()
                print(f"Current time: {time.strftime('%M:%S', time.gmtime(self.current_time))} of {time.strftime('%M:%S', time.gmtime(self.duration))}")

            # Playlist streams do not support media data
            if self.is_playlist:
                continue

            now_playing = self.media.get_meta(12)
            if now_playing == previously_playing:
                continue

            # Display the now playing track and record the previously playing track
            print("Now playing", now_playing)
            previously_playing = now_playing

            # Display the currently playing track genre
            genre = self.media.get_meta(2)
            if genre:
                print("Genre:", genre)
        return self.player.audio_get_track_description()

    def download_stream(self, file_name: str="", playlist_name: str="", download_only_default: bool=False) -> str:
        # Return if there is no default stream
        if not self.default_stream:
            print("Can't download radio stream; there is no default stream!")
            return None

        # Playlist defaults to "Downloaded Tracks" for YouTube audio streams and "Podcasts" for other stream types
        if not playlist_name:
            playlist_name = "Downloaded Tracks" if self.youtube_streams else "Podcasts"

        base_path = Path(os.getcwd()).parent.absolute() if "src" in os.getcwd() else os.getcwd()
        playlist_dir = os.path.join(base_path, "data", "playlists", playlist_name)
        # If the directory does not exist, create a new directory
        if not os.path.exists(playlist_dir):
            os.makedirs(playlist_dir)

        if self.youtube_streams:
            # Audio quality (bitrate) does not have a noticeable effect on the download times or sizes.
            # Using Ultra or High is preferable in most circumstances
            AUDIO_QUALITY = {"Ultra" : 0, "High" : 1, "Medium" : 2, "Low" : -1}

            # Download best stream and set filepath
            video = self.youtube_streams[AUDIO_QUALITY.get("Ultra")]
            file_path = os.path.join(playlist_dir, video.default_filename)
            file_extension = os.path.splitext(video.default_filename)[-1]
            file_path_mp3 = file_path.replace(file_extension, ".mp3")

            # Check if the file already exists
            if os.path.exists(file_path_mp3):
                print("This track was already downloaded to the specified playlist!")
                return file_path_mp3

            video.download(playlist_dir)

            # Use moviepy to convert an mp4 to an mp3 with metadata support. Delete mp4 afterwards
            audio_clip = AudioFileClip(file_path)
            audio_clip.write_audiofile(file_path_mp3, verbose=False, logger=None)
            audio_clip.close()
            os.remove(file_path)
            file_path = file_path_mp3

            # Update the file metadata according to YouTube video details
            with open(file_path, 'r+b') as file:
                media_file = mutagen.File(file, easy=True)
                media_file["title"] = self.title
                media_file["artist"] = self.artist
                # media_file["album"] = playlist_name
                media_file.save(file)

            return file_path

        # If file name is not overriden, use webite title from specified URL
        if not file_name:
            file_name = self.title
        file_path = os.path.join(playlist_dir, f"{file_name}.mp3")

        # Check if the file already exists
        if os.path.exists(file_path):
            print("This track was already downloaded to the specified playlist!")
            return file_path

        stream_to_download = None
        # Supported stream types to download
        supported_extensions = [".mp3", ".aac", ".ogg", ".m4a", ".wav", ".mpeg"]
        # If the default stream does not match one of the supported stream extensions
        if not Stream.is_supported_stream(self.default_stream, supported_extensions) and not self.youtube_streams:
            if download_only_default:
                print("Can't download radio stream; there are no supported streams!")
                return None
            # If download_only_default is set to false, check for other supported streams
            for stream in self.streams:
                if stream == self.default_stream:
                    continue
                if Stream.is_supported_stream(stream, supported_extensions):
                    stream_to_download = stream
                    break
            else:
                # If none of the streams are supported (the for loop ends without breaking)
                print("Can't download radio stream; there are no supported streams!")
                return None
        else:
            # If the default stream is a supported stream
            stream_to_download = self.default_stream

        # Downloading the stream
        stream_request = requests.get(stream_to_download, stream=True)

        with open(file_path, "wb") as f:
            try:
                # Write each chunk of the stream content to the created file
                for block in stream_request.iter_content(1024):
                    f.write(block)
                return file_path
            except Exception:
                return None

youtube = Stream("https://www.youtube.com/watch?v=wEGOxgfdRVc")
youtube.download_stream()
youtube.play_default_stream()

nytimes_podcast = Stream("https://www.nytimes.com/2022/03/14/podcasts/the-daily/ukraine-russia-family-misinformation.html")
nytimes_podcast.download_stream()
nytimes_podcast.play_default_stream()

google_podcast = Stream("https://podcasts.google.com/feed/aHR0cHM6Ly9mZWVkcy5tZWdhcGhvbmUuZm0vYXJ0Y3VyaW91c3BvZGNhc3Q")
google_podcast.download_stream()
google_podcast.play_default_stream()

apple_podcast = Stream("https://podcasts.apple.com/us/podcast/american-radical/id1596796171")
apple_podcast.download_stream()
apple_podcast.play_default_stream()

iheart_podcast = Stream("https://www.iheart.com/podcast/105-stuff-you-should-know-26940277/episode/selects-a-brief-overview-of-punk-94043727/")
iheart_podcast.play_default_stream()

cbc_news_podcast = Stream("https://www.cbc.ca/listen/cbc-podcasts/1057-welcome-to-paradise")
cbc_news_podcast.play_default_stream()

cnn_news_radio = Stream("https://www.cnn.com/audio")
cnn_news_radio.download_stream()
cnn_news_radio.play_default_stream()

abc_news_radio = Stream("https://www.abc.net.au/news/newsradio/")
abc_news_radio.play_default_stream()

dance_wave_radio = Stream("", ["http://yp.shoutcast.com/sbin/tunein-station.xspf?id=1631097"])
dance_wave_radio.play_default_stream()

antenne_bayerne_radio = Stream("", ["http://yp.shoutcast.com/sbin/tunein-station.m3u?id=99497996"])
antenne_bayerne_radio.play_default_stream()

virgin_radio = Stream("https://www.iheart.com/live/999-virgin-radio-7481/")
virgin_radio.play_default_stream()

iheart_radio = Stream("https://www.iheart.com/live/iheartradio-top-20-7556/")
iheart_radio.play_default_stream()

mnm_radio = Stream("", ["http://icecast.vrtcdn.be/mnm-high.mp3"])
mnm_radio.play_default_stream()

jbfm_radio = Stream("", ["http://playerservices.streamtheworld.com/api/livestream-redirect/JBFMAAC1.aac"])
jbfm_radio.play_default_stream()

virgin_radio_broken = Stream("", ["https://www.iheart.com/live/999-virgin-radio-7481/"])
virgin_radio_broken.play_default_stream()

'''
Helpful Resources
https://stackoverflow.com/questions/19377262/regex-for-youtube-url
https://www.olivieraubert.net/vlc/python-ctypes/doc/vlc.MediaListPlayer-class.html
Python vlc: https://www.olivieraubert.net/vlc/python-ctypes/, https://github.com/oaubert/python-vlc
'''