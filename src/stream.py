import os
import re
import urllib.request
import time
from pathlib import Path
from enum import Enum
from typing import Any, Optional

import vlc
import requests
from bs4 import BeautifulSoup

from pytube import YouTube
from moviepy.editor import AudioFileClip
import mutagen

from audio import Audio

class Stream(Audio):
    """
    Supports radio streaming, podcast streaming, and YouTube audio streams.
    Also supports downloading streams
    """

    def __init__(self, url: str, streams_override: list[str]=None, title_override:str=None) -> None:
        """
        Parameters
        ----------
        url : str
            The website url to extract streams from
        streams_override : list[str], optional
            The urls of streams that are passed in manually
        album : str
            The playlist artist
        title_override : str, optional
            Overrides the track title.
            Otherwise, extracts the track title from the website url or original source
        """
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
            except Exception as e:
                print(f"Error: {e}")
                if not title_override:
                    self.title = "New Radio Station"

    @staticmethod
    def is_stream_playlist(stream_url: str) -> bool:
        """
        Check if a stream matches a playlist type

        Parameters
        ----------
        stream_url : str
            The url of the stream

        Returns
        -------
        bool
            if the stream is a playlist type
        """
        # Create a set of playlist url extensions
        playlist_exts = {"pls", "m3u", "xspf"}
        # Get the first 4 characters of a url extension
        ext = stream_url.rpartition(".")[-1][:4]
        # Remove trailing characters that aren't part of the extension
        for char in "/?&#":
            ext = ext.replace(char, "")
        # Determine if the stream is a playlist
        return ext in playlist_exts

    @staticmethod
    def check_stream_validity(stream_url: str) -> tuple[bool, vlc.State]:
        """
        Checks if a stream is valid and is able to be played by the VLC player.

        Parameters
        ----------
        stream_url : str
            The url of the stream

        Returns
        -------
        bool
            if the stream is valid
        vlc.State
            the state of the VLC player while checking the stream
        """
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
            # Wait until the vlc player starts playing
            condition, current_time = True, 0.0
            while condition:
                condition, current_time = Stream.wait_while(not player.is_playing(), current_time)

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
    def is_supported_stream(stream_url: str, supported_extensions: list[str]) -> bool:
        """Checks if the stream url contains any of the specified extensions"""
        return any(extension in stream_url for extension in supported_extensions)

    @staticmethod
    def get_streams(url: str) -> tuple[list[str], Optional[Any]]:
        """
        Returns a list of stream urls (and optionally, a list of YouTube audio streams) from a URL.

        Parameters
        ----------
        url : str
            The url of website to extract the streams from

        Returns
        -------
        list[str]
            a list of stream urls
        list[Stream], optional
            an optional list of YouTube streams
        """
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

        regex_terms = {"stream", "file", "@id", "fileURL", "streamURL", "mediaURL", "associatedMedia"}
        # Return the stream urls that match the regular expressions
        for term in regex_terms:
            if streams:
                return streams, youtube_streams
            streams = re.findall(f"{term}\":\"(.*?)\"", raw_file)

        # Search terms for Apple Podcasts, Google Podcasts, etc.
        specialized_regex_terms = {r"assetUrl\\\":\\\"(.*?)\"" , r"jsdata=\"Kwyn5e;(.*?);", r"url\":\"(.*?)\"", r"src=\"(.*?)\"", r"href=\"(.*?)\""}
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
    def get_youtube_audio_streams(url: str) -> tuple[list[str], list[Any]]:
        """
        Get streams and stream urls ordered by bitrate in descending order (highest bitrate first).

        Parameters
        ----------
        url : str
            The YouTube video url to extract the streams from

        Returns
        -------
        list[str]
            a list of stream urls
        list[Stream]
            a list of YouTube streams
        """
        yt = YouTube(url)
        youtube_streams = yt.streams.filter(only_audio=True).order_by("bitrate").desc()
        streams = [stream.url for stream in youtube_streams]
        return streams, youtube_streams

    @staticmethod # Move to another class/file
    def wait_while(condition: bool, current_time: float, time_out: float=5, increment_steps: int=100) -> tuple[bool, float]:
        """
        Wait while a condition is true until the function times out.
        You need to use this method as a conditional in a while loop

        Implementation
        ----------
        condition, current_time = True, 0.0

        while condition:
            condition, current_time = Stream.wait_while(condition, current_time, ...)

        Parameters
        ----------
        condition : bool
            The condition to check for
        current_time : float
            The current time counter (to check for a time out)

        Returns
        -------
        bool
            whether the condition is True and it hasn't timed out yet
        float
            the updated current time counter (to check for a time out)
        """
        current_time = 0.0
        increment = time_out / float(increment_steps)

        if condition and current_time < time_out:
            current_time += increment
            time.sleep(increment)
            return True, current_time
        return False, current_time

    def get_youtube_stream_bitrates(self) -> Optional[list[str]]:
        """
        Returns a list of the average bitrate of the streams in the same order (if there are supported YouTube streams)

        Returns
        -------
        list[str], optional
            a list of stream url average bitrates, ordered
        """
        if self.youtube_streams:
            return [stream.abr for stream in self.youtube_streams]
        return None

    def set_default_stream(self, stream_index: int=0) -> None:
        """
        Set the stream that will be played by default

        Parameters
        ----------
        stream_index : int, optional
            The index of the stream in the list of stream urls to set as default.
            If not specified, it is defaulted to the first stream.

        Raises
        ------
        IndexError
            If the stream_index exceeds the value of the final stream index
        """
        if stream_index < len(self.streams):
            self.default_stream = self.streams[stream_index]
            # Determine if the default stream is a playlist
            self.is_playlist = Stream.is_stream_playlist(self.default_stream)
        else:
            self.default_stream = None
            raise IndexError

    def add_stream_manual(self, stream_url: str, default: bool=True) -> int:
        """
        Manually add a stream and check if it is valid

        Parameters
        ----------
        stream_url : str
            The stream url to add
        default : bool, optional
            Set the added stream as the default stream to use.
            If nor specified, it is defaulted to True

        Returns
        -------
        int
            The index of the added stream.
            Returns 1 if the stream could not be added
        """

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

    def play(self) -> None:
        self.play_default_stream()

    def play_default_stream(self) -> None:
        """Play the default stream using the VLC media player"""
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
        # Wait until the vlc player starts playing
        condition, current_time = True, 0.0
        while condition:
            condition, current_time = Stream.wait_while(not self.player.is_playing(), current_time)

        # Get the current track duration
        if not self.is_playlist:
            self.duration = self.player.get_length() // 1000

        # Record the previously playing track
        previously_playing = None

        # While the stream is still playing
        # Alternatively, use "self.player.get_state() != vlc.State.Ended" without the prior wait while
        while self.player.is_playing():
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

    def download_stream(self, file_name: str="", download_only_default: bool=False) -> Optional[str]:
        """
        Download the default or supported stream to a playlist

        Parameters
        ----------
        file_name : str, optional
            The name of the downloaded music file.
            If not specified, the extracted url title or YouTube video title is used instead.
            It is preferable to override the default if the input is a stream url override, otherwise, the title can be extracted from the website or YouTube url
        playlist_name : str, optional
            The name of the playlist that the downloaded track is a part of.
            If not specified, it will be defaulted to either "Downloaded Tracks" or "Podcasts"
        download_only_default : bool, optional
            If set to false, other supported streams will be checked for compatibility if the default stream is not a supported type.
            Otherwise, the program will only attempt to download the default stream

        Returns
        -------
        string, optional
            The downloaded file path
        """
        # Return if there is no default stream
        if not self.default_stream:
            print("Can't download radio stream; there is no default stream!")
            return None

        download_dir = os.path.abspath(os.path.join("data", "tracks"))

        if self.youtube_streams:
            # Download best stream and set filepath
            video = self.youtube_streams[AudioQuality.ULTRA.value]
            file_path = os.path.join(download_dir, video.default_filename)
            file_extension = os.path.splitext(video.default_filename)[-1]
            file_path_mp3 = file_path.replace(file_extension, ".mp3")

            # Check if the file already exists
            if os.path.exists(file_path_mp3):
                print("This track was already downloaded to the specified playlist!")
                return file_path_mp3

            video.download(download_dir)

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
        file_path = os.path.join(download_dir, f"{file_name}.mp3")

        # Check if the file already exists
        if os.path.exists(file_path):
            print("This track was already downloaded to the specified playlist!")
            return file_path

        stream_to_download = None
        # Supported stream types to download
        supported_extensions = {".mp3", ".aac", ".ogg", ".m4a", ".wav", ".mpeg"}
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
            # Write each chunk of the stream content to the created file
            for block in stream_request.iter_content(1024):
                f.write(block)
            return file_path


class AudioQuality(Enum):
    """
    Audio quality (bitrate) does not have a noticeable effect on the download times or sizes.
    Using Ultra or High is preferable in most circumstances.
    """
    ULTRA = 0
    HIGH = 1
    MEDIUM = 2
    LOW = -1

from database import PlaylistManager

def main():
    playlist_manager = PlaylistManager()
    playlist_manager.close_session(False)
    liked_songs = playlist_manager.get_or_create_playlist("Liked Songs")

    for track in liked_songs.tracks:
        print(track.title)
        Stream(track.stream.url).play_default_stream()

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


if __name__ == "__main__":
    main()

"""
Helpful Resources
https://stackoverflow.com/questions/19377262/regex-for-youtube-url
https://www.olivieraubert.net/vlc/python-ctypes/doc/vlc.MediaListPlayer-class.html
Python vlc: https://www.olivieraubert.net/vlc/python-ctypes/, https://github.com/oaubert/python-vlc
"""