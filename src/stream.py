import os
import re
import time
import requests
from bs4 import BeautifulSoup

from enum import Enum
from typing import Any, Callable, Optional

import pafy
import vlc
from pytube import YouTube
from moviepy.editor import AudioFileClip
import mutagen

from database import PlaylistManager

class StreamUtility:
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
            response = requests.get(stream_url, verify=False)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Return the HTTP status code error that was sent with the response (e.g. 404, 501, ...)
            print(f"HTTP Error: {e}")
        except requests.exceptions.RequestException as e:
            # Not an HTTP-specific error (e.g. connection refused)
            print(f"URL Error: {e}")
        except Exception as e:
            # Not an HTTP-specific or RequestException error (e.g. unknow url type)
            print(f"Error: {e}")
        else:
            # Start a vlc instance and try playing the stream
            instance = vlc.Instance()
            player = instance.media_player_new()
            player.audio_set_mute(True)

            is_playlist = StreamUtility.is_stream_playlist(stream_url)
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
                condition, current_time = StreamUtility.wait_while(not player.is_playing(), current_time)

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
        """
        Checks if the stream url contains any of the specified extensions

        Parameters
        ----------
        stream_url : str
            The url of the stream
        supported_extensions: list[str]
            A list of supported extensions (e.g. ".mp3")

        Returns
        -------
        bool
            if the stream url contains any of the supported extensions
        """
        return any(extension in stream_url for extension in supported_extensions)

    @staticmethod
    def is_youtube_url(url: str) -> bool:
        """
        Returns whether or not a url is a YouTube video link.

        Parameters
        ----------
        url : str
            The url to check

        Returns
        -------
        bool
            whether or not the url is a YouTube video link
        """

        # Source for YouTube URL regex: https://stackoverflow.com/a/37704433
        youtube_regex = "^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
        return re.search(youtube_regex, url)

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
        if StreamUtility.is_youtube_url(url):
            streams, youtube_streams = StreamUtility.get_youtube_audio_streams(url)
            return streams, youtube_streams

        # Try opening the url
        response = requests.get(url, verify=False)
        try:
            response.raise_for_status()
        except Exception as e:
            print(f"Could not open the specified URL. Error: {e}")
            return streams, youtube_streams

        # Decoding the page source
        response.encoding = response.apparent_encoding
        raw_file = response.text

        supported_extensions = {".wma", ".xspf", ".pls", ".m3u8", ".m3u", ".hls", ".mp3", ".aac", ".ogg", ".m4a", ".wav"}
        regex_terms = {"stream", "file", "@id", "fileURL", "streamURL", "mediaURL", "associatedMedia"}
        # Return the stream urls that match the regular expressions
        for term in regex_terms:
            if streams:
                return streams, youtube_streams
            streams = re.findall(f"{term}\":\"(.*?)\"", raw_file)

            # Remove all results without the supported extensions (Due to these regular expressions being very generalized)
            streams[:] = [stream for stream in streams if StreamUtility.is_supported_stream(stream, supported_extensions)]

        # Search terms for Apple Podcasts, Google Podcasts, etc.
        specialized_regex_terms = {r"assetUrl\\\":\\\"(.*?)\"" , r"jsdata=\"Kwyn5e;(.*?);", r"url\":\"(.*?)\"", r"src=\"(.*?)\"", r"href=\"(.*?)\""}
        for term in specialized_regex_terms:
            if streams:
                return streams, youtube_streams
            streams = re.findall(term, raw_file)

            # Remove all results without the supported extensions (Due to these regular expressions being very generalized)
            streams[:] = [stream for stream in streams if StreamUtility.is_supported_stream(stream, supported_extensions)]
        return streams, youtube_streams

    @staticmethod
    def get_stream_duration(stream_url: str) -> int:
        """
        Returns the duration of the stream in seconds

        Parameters
        ----------
        stream_url : str
            The url of the stream

        Returns
        -------
        int
            the duration of the stream in seconds
        """
        instance = vlc.Instance()
        player = instance.media_player_new()
        player.audio_set_mute(True)

        is_playlist = StreamUtility.is_stream_playlist(stream_url)
        if is_playlist:
            player = instance.media_list_player_new()
            media = instance.media_list_new([stream_url])
            player.set_media_list(media)
        else:
            media = instance.media_new(stream_url)
            player.set_media(media)

        player.play()

        # Wait until the vlc player starts playing
        condition, current_time = True, 0.0
        while condition:
            condition, current_time = StreamUtility.wait_while(not player.is_playing(), current_time)

        if not is_playlist:
            duration = player.get_length() // 1000

        player.stop()
        return duration

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
    def wait_while(condition: bool, current_time: float, time_out: float=5.0, increment_steps: int=100) -> tuple[bool, float]:
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


class StreamData:
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
        self.player = None
        if not streams_override:
            self.url = url
            # Get streams from url and if available, the youtube streams
            self.streams, self.youtube_streams = StreamUtility.get_streams(url)
            self.set_default_stream()

            if not self.youtube_streams:
                # Get website title
                soup = BeautifulSoup(requests.get(url, verify=False).text, features="html.parser")
                # Get stream title and remove white spaces and special/escape characters
                self.title = soup.title.text.replace("|", "").split()
                self.title = " ".join(self.title)
                self.album = self.title
                self.artist = "Unknown"
                self.duration = StreamUtility.get_stream_duration(self.default_stream)
            else:
                yt = YouTube(self.url)

                # Get YouTube song metadata if it exists
                if yt.metadata:
                    if type(yt.metadata) is list:
                        metadata = yt.metadata[0]
                    elif type(yt.metadata.metadata) is list and yt.metadata.metadata:
                        metadata = yt.metadata.metadata[0]
                    elif yt.metadata.metadata:
                        metadata = yt.metadata.metadata
                    else:
                        metadata = None
                else:
                    metadata = None

                self.title = metadata.get("Song") if metadata else None
                if not self.title:
                    self.title = yt.title
                self.artist = metadata.get("Artist") if metadata else None
                if not self.artist:
                    self.artist = yt.author
                self.album = metadata.get("Album") if metadata else None
                if not self.album:
                    self.album = self.title
                self.duration = yt.length
        else:
            # Assign streams if streams are valid
            if StreamUtility.check_stream_validity(streams_override[0])[0]:
                self.streams = streams_override
            self.set_default_stream()

            try:
                # Try getting a website url from the default stream
                url = requests.get(self.default_stream, stream=True, verify=False).headers.get("icy-url")
                # Get website title
                soup = BeautifulSoup(requests.get(url, verify=False).text, features="html.parser")
                # Get stream title and remove white spaces and special/escape characters
                self.title = " ".join(soup.title.text.split())
            except Exception as e:
                print(f"Error: {e}")
                if not title_override:
                    self.title = "New Radio Station"

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
            self.is_playlist = StreamUtility.is_stream_playlist(self.default_stream)
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
        valid_stream = StreamUtility.check_stream_validity(stream_url)[0]
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
        if not StreamUtility.is_supported_stream(self.default_stream, supported_extensions) and not self.youtube_streams:
            if download_only_default:
                print("Can't download radio stream; there are no supported streams!")
                return None
            # If download_only_default is set to false, check for other supported streams
            for stream in self.streams:
                if stream == self.default_stream:
                    continue
                if StreamUtility.is_supported_stream(stream, supported_extensions):
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
        stream_request = requests.get(stream_to_download, stream=True, verify=False)

        with open(file_path, "wb") as f:
            # Write each chunk of the stream content to the created file
            for block in stream_request.iter_content(1024):
                f.write(block)
            return file_path

    def add_to_playlist(self, playlist_name: str) -> None:
        """
        Creates a new database Track object and populates it with information from the StreamData obejct such as title, artist, duration, etc.
        Then, adds this Track object to the playlist specified (Creates a new playlist with the name if it doesn't exist)

        Parameters
        ----------
        playlist_name : str
            The name of the playlist to add the track to

        Returns
        -------
        None
        """
        playlist_manager = PlaylistManager()
        playlist_manager.open_session()
        playlist = playlist_manager.get_or_create_playlist(playlist_name)

        # Check whether the stream is a YouTube stream, since they are temporary streams.
        # If so, store the video url instead
        stream = self.default_stream if not self.youtube_streams else self.url

        track = playlist_manager.create_and_add_track_to_playlist(self.title, self.artist, self.album, self.duration, stream, playlist)

        if playlist.downloaded:
            path = self.download_stream()
            if path:
                track.path = path

        playlist_manager.commit_session()
        playlist_manager.close_session()

    def add_to_liked_songs(self) -> None:
        """
        Creates a new database Track object and populates it with information from the StreamData obejct such as title, artist, duration, etc.
        Then, adds this Track object to the "Liked Songs" Playlist

        Returns
        -------
        None
        """
        self.add_to_playlist("Liked Songs")

class Stream():
    def __init__(self, url: str, time_elapsed_callback: Optional[Callable]=None) -> None:
        """
        Parameters
        ----------
        url : str
            The stream url
        time_elapsed_callback : Callable, optional
            The function that is called when the stream is played and the time changes
        """
        if StreamUtility.is_youtube_url(url):
            stream = pafy.new(url).getbestaudio().url
        else:
            stream = url

        self.stream = stream
        self.time_elapsed_callback = time_elapsed_callback
        self.is_playlist = StreamUtility.is_stream_playlist(self.stream)
        self.looping = False

        # Create a vlc instance and player
        self.vlc_instace = vlc.Instance()
        self.player = self.vlc_instace.media_player_new()

    def play(self, continuous_play: bool=False, start_time: float=0.0) -> None:
        """
        Play a stream using the VLC media player

        Parameters
        ----------
        continuous_play : bool
            Whether or not the program should be paused while the content is playing.
            Prints track info for supported streams
        start_time: float
            The time the track should start playing at in seconds

        Returns
        -------
        None
        """

        # self.player.audio_set_mute(False)

        if self.is_playlist:
            # Set the default stream playlist as the playable media list
            self.player = self.vlc_instace.media_list_player_new()
            self.media = self.vlc_instace.media_list_new([self.stream])
            self.player.set_media_list(self.media)
        else:
            # Set the default stream as the playable media
            self.media = self.vlc_instace.media_new(self.stream)
            self.player.set_media(self.media)

        self.vlc_event_manager = self.player.event_manager()
        self.vlc_event_manager.event_attach(vlc.EventType.MediaPlayerTimeChanged, self._media_time_elapsed)

        self.player.play()
        # Wait until the vlc player starts playing
        condition, current_time = True, 0.0
        while condition:
            condition, current_time = StreamUtility.wait_while(not self.player.is_playing(), current_time)

        # Set the start time in ms
        if start_time > 0.0:
            self.player.set_time(int(start_time * 1000.0))

        # Get the current track duration
        if not self.is_playlist:
            self.duration = self.player.get_length() // 1000.0

        # Record the previously playing track
        previously_playing = None

        if not continuous_play:
            return

        # While the stream is still playing
        # Alternatively, use "self.player.get_state() != vlc.State.Ended" without the prior wait while
        while self.player.is_playing():
            time.sleep(1)

            # Debug information
            if not self.is_playlist:
                print(f"Percent: {round(self.player.get_position() * 100, 2)}%")
                self.current_time = self.player.get_time() / 1000.0
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

    def _media_time_elapsed(self, event) -> None:
        """
        A private callback method for vlc.EventType.MediaPlayerTimeChanged

        Parameters
        ----------
        event : vlc.Event
            The callback event information

        Returns
        -------
        None
        """
        print(type(event))
        current_time = self.player.get_time() / 1000.0
        current_position = self.player.get_position()

        if self.time_elapsed_callback:
            self.time_elapsed_callback(current_time, current_position)

    def stop(self) -> None:
        """
        Stops audio playback

        Returns
        -------
        None
        """
        if self.player:
            self.player.stop()

    def pause(self) -> None:
        """
        Pauses audio playback

        Returns
        -------
        None
        """
        if self.player:
            self.player.pause()

    def unpause(self) -> None:
        """
        Unpauses audio playback

        Returns
        -------
        None
        """
        if self.player:
            self.player.play()

    def skip_forwards(self, seconds: float) -> None:
        """
        Skip forwards in the current audio playback

        Parameters
        ----------
        seconds : float
            The amount of time in seconds to skip forwards

        Returns
        -------
        None
        """
        if not self.player:
            return

        current_time = self.player.get_time()
        time_increment = int(seconds * 1000.0)
        self.player.set_time(current_time + time_increment)

    def skip_backwards(self, seconds: float) -> None:
        """
        Skip backwards in the current audio playback

        Parameters
        ----------
        seconds : float
            The amount of time in seconds to skip backwards

        Returns
        -------
        None
        """
        if not self.player:
            return

        current_time = self.player.get_time()
        time_increment = int(seconds * 1000.0)
        self.player.set_time(current_time - time_increment)

    def set_rate(self, rate: float=1.0) -> None:
        """
        Set the audio playback rate (multiplicative factor)

        Parameters
        ----------
        rate : float
            The rate at which the audio plays at

        Returns
        -------
        None
        """
        if not self.player:
            return

        self.player.set_rate(rate)

    def set_loop(self, looping: bool=True) -> None:
        """
        Sets whether the current track should loop

        Parameters
        ----------
        looping : bool
            Whether or not the track should loop

        Returns
        -------
        None
        """
        if looping == self.looping:
            return

        self.looping = looping
        self.vlc_instace = vlc.Instance("--input-repeat=999999" if self.looping else "")

        if not self.player:
            return

        current_time = self.player.get_time() / 1000.0
        self.player.stop()
        self.player = self.vlc_instace.media_player_new()
        self.play(start_time=current_time)


class AudioQuality(Enum):
    """
    Audio quality (bitrate) does not have a noticeable effect on the download times or sizes.
    Using Ultra or High is preferable in most circumstances.
    """
    ULTRA = 0
    HIGH = 1
    MEDIUM = 2
    LOW = -1

def test():
    youtube = StreamData("https://www.youtube.com/watch?v=wEGOxgfdRVc")
    Stream(youtube.default_stream).play(True)

    google_podcast = StreamData("https://podcasts.google.com/feed/aHR0cHM6Ly9mZWVkcy5tZWdhcGhvbmUuZm0vYXJ0Y3VyaW91c3BvZGNhc3Q")
    google_podcast.download_stream()
    Stream(google_podcast.default_stream).play(True)

    apple_podcast = StreamData("https://podcasts.apple.com/us/podcast/american-radical/id1596796171")
    apple_podcast.download_stream()
    Stream(apple_podcast.default_stream).play(True)

    iheart_podcast = StreamData("https://www.iheart.com/podcast/105-stuff-you-should-know-26940277/episode/selects-a-brief-overview-of-punk-94043727/")
    Stream(iheart_podcast.default_stream).play(True)

    cbc_news_podcast = StreamData("https://www.cbc.ca/listen/cbc-podcasts/1057-welcome-to-paradise")
    Stream(cbc_news_podcast.default_stream).play(True)

    cnn_news_radio = StreamData("https://www.cnn.com/audio")
    Stream(cnn_news_radio.default_stream).play(True)

    abc_news_radio = StreamData("https://www.abc.net.au/news/newsradio/")
    Stream(abc_news_radio.default_stream).play(True)

    dance_wave_radio = StreamData("", ["http://yp.shoutcast.com/sbin/tunein-station.xspf?id=1631097"])
    Stream(dance_wave_radio.default_stream).play(True)

    antenne_bayerne_radio = StreamData("", ["http://yp.shoutcast.com/sbin/tunein-station.m3u?id=99497996"])
    Stream(antenne_bayerne_radio.default_stream).play(True)

    virgin_radio = StreamData("https://www.iheart.com/live/999-virgin-radio-7481/")
    Stream(virgin_radio.default_stream).play(True)

    iheart_radio = StreamData("https://www.iheart.com/live/iheartradio-top-20-7556/")
    Stream(iheart_radio.default_stream).play(True)

    mnm_radio = StreamData("", ["http://icecast.vrtcdn.be/mnm-high.mp3"])
    Stream(mnm_radio.default_stream).play(True)

    jbfm_radio = StreamData("", ["http://playerservices.streamtheworld.com/api/livestream-redirect/JBFMAAC1.aac"])
    Stream(jbfm_radio.default_stream).play(True)

    # NYTimes Podcasts are now inaccessible
    # nytimes_podcast = StreamData("https://www.nytimes.com/2022/03/14/podcasts/the-daily/ukraine-russia-family-misinformation.html")
    # Stream(nytimes_podcast.default_stream).play(True)

if __name__ == "__main__":
    test()

"""
Helpful Resources
https://www.olivieraubert.net/vlc/python-ctypes/doc/vlc.MediaListPlayer-class.html
Python vlc: https://www.olivieraubert.net/vlc/python-ctypes/, https://github.com/oaubert/python-vlc
"""