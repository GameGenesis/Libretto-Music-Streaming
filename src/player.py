from typing import Optional
import config
import time

import lyricsgenius as lg
from youtubesearchpython import VideosSearch

from PIL import ImageTk, Image, ImageDraw
import requests
from io import BytesIO

from tkinter import Canvas, PhotoImage

from stream import Stream, StreamData
from database import Playlist, Track, playlist_manager


genius = None

gui_canvas = None
gui_elapsed_time_text = None
gui_track_slider = None
past_time = 0

gui_heart_button, gui_heart_empty_image, gui_heart_full_image = None, None, None
gui_loop_button, gui_no_loop_button_image, gui_loop_button_image = None, None, None
gui_play_button, gui_play_button_image, gui_pause_button_image = None, None, None
gui_track_title_text, gui_track_artist_text, gui_total_time_text = None, None, None
gui_album_cover_art, gui_album_cover_art_image = None, None

looping = False
playing = False
stream = None


def init(canvas: Canvas, elapsed_time_text: int, track_slider: "Slider",
    heart_button: int, heart_empty_image: PhotoImage, heart_full_image: PhotoImage,
    loop_button: int, no_loop_button_image: PhotoImage, loop_button_image: PhotoImage,
    play_button: int, play_button_image: PhotoImage, pause_button_image: PhotoImage,
    track_title_text: int, track_artist_text: int, total_time_text: int,
    album_cover_art: int, album_cover_art_image: PhotoImage) -> None:
    """
    Pass in the tkinter GUI for referencing

    Parameters
    ----------
    canvas : Canvas
        The main GUI canvas
    elapsed_time_text : int
        The elapsed time text canvas item
    track_slider : Slider
        The elapsed time slider
    heart_button : int
        The heart button canvas item
    heart_empty_image : PhotoImage
        The empty heart image
    heart_full_image : PhotoImage
        The full heart image
    loop_button : int
        The loop button canvas item
    no_loop_button_image : PhotoImage
        The inactive loop image
    loop_button_image : PhotoImage
        The active loop image
    play_button : int
        The play/pause button canvas item
    play_button_image : PhotoImage
        The play button image
    pause_button_image : PhotoImage
        The pause button image
    track_title_text : int
        The track title text canvas item
    track_artist_text : int
        The track artist text canvas item
    total_time_text : int
        The track total duration text canvas item
    album_cover_art : int
        The track album cover art image canvas item
    album_cover_art_image : PhotoImage
        The placeholder track album cover art

    Returns
    -------
    None
    """
    global genius
    global gui_canvas, gui_elapsed_time_text, gui_track_slider, gui_heart_button, gui_heart_empty_image, gui_heart_full_image
    global gui_loop_button, gui_no_loop_button_image, gui_loop_button_image
    global gui_play_button, gui_play_button_image, gui_pause_button_image
    global gui_track_title_text, gui_track_artist_text, gui_total_time_text
    global gui_album_cover_art, gui_album_cover_art_image

    genius = lg.Genius(config.GENIUS_ACCESS_TOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"], remove_section_headers=True, verbose=False)

    gui_canvas = canvas
    gui_elapsed_time_text = elapsed_time_text
    gui_track_slider = track_slider
    gui_heart_button = heart_button
    gui_heart_empty_image = heart_empty_image
    gui_heart_full_image = heart_full_image
    gui_loop_button = loop_button
    gui_no_loop_button_image = no_loop_button_image
    gui_loop_button_image = loop_button_image
    gui_play_button = play_button
    gui_play_button_image = play_button_image
    gui_pause_button_image = pause_button_image
    gui_track_title_text = track_title_text
    gui_track_artist_text = track_artist_text
    gui_total_time_text = total_time_text
    gui_album_cover_art = album_cover_art
    gui_album_cover_art_image = album_cover_art_image

def toggle_track_like(track: Track) -> None:
    """
    Add or remove a track from Liked Songs

    Parameters
    ----------
    track : Track
        The track database object to add or remove from the "Liked Songs" playlist

    Returns
    -------
    None
    """
    global gui_canvas, gui_heart_button, gui_heart_empty_image, gui_heart_full_image

    liked_track = playlist_manager.track_is_liked(track)
    if liked_track:
        playlist_manager.remove_track_from_liked_songs(track)
    else:
        playlist_manager.add_track_to_liked_songs(track)

    liked_track = not liked_track
    gui_canvas.itemconfig(gui_heart_button, image=gui_heart_full_image if liked_track else gui_heart_empty_image)

def skip_backwards() -> None:
    """
    Skips the current playing track backwards by 10s

    Returns
    -------
    None
    """
    if not stream:
        return

    stream.skip_backwards(10.0)

def skip_forwards():
    """
    Skips the current playing track forwards by 10s

    Returns
    -------
    None
    """
    if not stream:
        return

    stream.skip_forwards(10.0)

def toggle_loop() -> None:
    """
    Toggles the current playing track from not looping to looping and vice versa.
    Also sets the loop button to match the track state

    Returns
    -------
    None
    """
    global looping
    global gui_canvas, gui_loop_button, gui_no_loop_button_image, gui_loop_button_image
    if not stream:
        return

    looping = not looping
    stream.set_loop(looping)

    gui_canvas.itemconfig(gui_loop_button, image=gui_loop_button_image if looping else gui_no_loop_button_image)

def configure_play_state() -> None:
    """
    Pauses or unpauses a track depending on the play state and
    configures the play/pause button according to whether the track is paused or not

    Returns
    -------
    None
    """
    global stream, playing
    global gui_canvas, gui_play_button, gui_play_button_image, gui_pause_button_image
    if playing:
        stream.unpause()
        gui_canvas.itemconfig(gui_play_button, image=gui_pause_button_image)
    else:
        stream.pause()
        gui_canvas.itemconfig(gui_play_button, image=gui_play_button_image)

def play_pause_track() -> None:
    """
    Plays or pauses a track and configures the play/pause button

    Returns
    -------
    None
    """
    global stream, playing
    global gui_canvas, gui_play_button, gui_play_button_image, gui_pause_button_image
    if not stream:
        return

    playing = not playing
    configure_play_state()

def _update_elapsed_time(current_time: float, current_position: float) -> None:
    """
    Private callback method to update the elapsed time text and the elapsed time slider

    Parameters
    ----------
    current_time : float
        The time that has passed since the start of the track
    current_position : float
        The fraction of the song that has passed (in decimal form)

    Returns
    -------
    None
    """
    global gui_canvas, gui_elapsed_time_text, past_time

    gui_canvas.itemconfig(gui_elapsed_time_text, text=Utils.get_formatted_time(int(current_time)))

    if int(current_time) != past_time:
        gui_track_slider.set_position(current_position)

    past_time = int(current_time)

def play_database_track(track_id: int) -> None:
    """
    Plays a track that is stored in a database

    Parameters
    ----------
    track_id : int
        The id of the track database object

    Returns
    -------
    None
    """
    if stream:
        stream.stop()

    track = playlist_manager.get_track(id=track_id)
    play_track(track)

def play_search_track(track_title: str, cover_art_url: str) -> None:
    """
    Plays a track from search results

    Parameters
    ----------
    track_title : str
        The full title of the track to search for
    cover_art_url : str
        The url for the cover art image

    Returns
    -------
    None
    """
    if stream:
        stream.stop()

    result = get_song_yt(track_title)

    track_id = StreamData(result["link"]).add_to_playlist()
    track = playlist_manager.get_track(id=track_id)

    playlist_manager.add_track_cover_art(track, cover_art_url)

    play_track(track)

def play_track(track: Track) -> None:
    global stream, playing, looping
    global gui_canvas, gui_heart_button, gui_heart_full_image, gui_heart_empty_image
    global gui_track_title_text, gui_track_artist_text, gui_total_time_text
    global gui_album_cover_art, gui_album_cover_art_image
    """
    Plays a track and updates current playing track info

    Parameters
    ----------
    track : Track
        The track database object to access information from and play

    Returns
    -------
    None
    """

    if track.cover_art_url:
        cover_art_image = create_image(track.cover_art_url, (54, 54))
        if cover_art_image:
            gui_canvas.images = list()
            gui_canvas.images.append(cover_art_image)
            gui_canvas.itemconfig(gui_album_cover_art, image=cover_art_image)
        else:
            gui_canvas.itemconfig(gui_album_cover_art, image=gui_album_cover_art_image)
    else:
        gui_canvas.itemconfig(gui_album_cover_art, image=gui_album_cover_art_image)

    liked_track = playlist_manager.track_is_liked(track)
    gui_canvas.itemconfig(gui_heart_button, image=gui_heart_full_image if liked_track else gui_heart_empty_image)
    gui_canvas.tag_bind(gui_heart_button, "<ButtonPress-1>", lambda event, track=track: toggle_track_like(track))

    title = Utils.truncate_string(track.title, 16)
    artist = Utils.truncate_string(track.artist, 16)

    gui_canvas.itemconfig(gui_track_title_text, text=title)
    gui_canvas.itemconfig(gui_track_artist_text, text=artist)

    track_duration = Utils.get_formatted_time(track.duration)
    gui_canvas.itemconfig(gui_total_time_text, text=track_duration)

    stream = Stream(track.stream.url, _update_elapsed_time)
    stream.set_loop(looping)
    stream.play()

    playing = True
    configure_play_state()

def get_playlist_info(playlist: Playlist) -> str:
    """
    Gets information about the tracks in the playlist

    Format: (number of songs, length)

    Parameters
    ----------
    playlist : Playlist
        The playlist from which to return information

    Returns
    -------
    str
        A formatted string with the information to display about the playlist
    """
    total_duration = playlist.get_total_duration()
    hours = total_duration // 3600
    mins = (total_duration - (hours * 3600)) // 60
    secs = (total_duration - (hours * 3600) - (mins * 60))

    playlist_length = playlist.get_length()
    formatted_length = f"{playlist_length} songs" if playlist_length > 1 else f"{playlist_length} song"
    formatted_time = f"{hours} hr {mins} min" if hours > 0 else f"{mins} min {secs} sec"
    playlist_information = f"{formatted_length}, {formatted_time}"
    return playlist_information

def search(search_term: str) -> dict:
    """
    Performs a Genius general search

    Parameters
    ----------
    search_term : str
        The term to search

    Returns
    -------
    dict
        A dictionary containing data about the search results
    """
    results = genius.search(search_term)
    return results

def get_song_yt(search_term: str) -> dict:
    """
    Performs a YouTube video search

    Parameters
    ----------
    search_term : str
        The term to search

    Returns
    -------
    dict
        A dictionary containing data about the search results
    """
    videosSearch = VideosSearch(search_term, limit = 1)
    result = videosSearch.result()["result"][0]
    return result

def create_image(image_url: str, size: tuple[int, int], radius: Optional[int]=None) -> PhotoImage:
    """
    Returns a created PhotoImage using an image url.
    Resizes the image to the specified size.
    Optionally, adds rounded corners to the created image.

    Parameters
    ----------
    image_url : str
        The image url
    size : tuple[int, int]
        The size of the created image
    radius: : int, optional
        The radius of the image corners

    Returns
    -------
    PhotoImage
        A tkinter PhotoImage
    """
    webimage = WebImage(image_url)
    if radius:
        webimage.add_corners(radius)
    webimage.resize(size)
    return webimage.get()


class Utils:
    @staticmethod
    def truncate_string(string: str, max_length: int, continuation_str: str="..") -> str:
        """
        Returns a string that is cut off to a certain length (including the continuation string)

        Parameters
        ----------
        string : str
            The original string to truncate
        max_length : int
            The max permissable length of the string (including the continuation string)

        Returns
        -------
        str
            The new truncated string
        """
        truncated_len = max_length-len(continuation_str)
        truncated_str = f"{string[:truncated_len]}{continuation_str}"
        return truncated_str if len(string) > max_length else string

    @staticmethod
    def split_list(list: list, size: int) -> list:
        """
        Splits a list into smaller-sized lists of a specified size

        Parameters
        ----------
        list : list
            The original list to split
        size : int
            The maximum number of elements in each sub-list

        Returns
        -------
        list
            The split list
        """
        return (list[index:index+size] for index in range(0, len(list), size))

    @staticmethod
    def get_formatted_time(seconds: int) -> str:
        """
        Returns a formatted time string in (m:ss) format from a seconds int

        Parameters
        ----------
        seconds : int
            The amount of time in seconds

        Returns
        -------
        str
            The formatted time string
        """
        return time.strftime('%#M:%S', time.gmtime(seconds))

    @staticmethod
    def get_unformatted_time(time_str: str) -> int:
        """
        Returns a the time in seconds from a formatted time string (h:m:s) or (m:s)

        Parameters
        ----------
        time_str : str
            The formatted time string

        Returns
        -------
        int
            The time in seconds
        """
        h = 0
        if time_str.count(":") == 1:
            m, s = time_str.split(":")
        else:
            h, m, s = time_str.split(":")
        return int(h) * 3600 + int(m) * 60 + int(s)

    @staticmethod
    def clamp(value: float, min_value: float, max_value: float) -> float:
        """
        Returns a value clamped between a min and max

        Parameters
        ----------
        value : float
            The original value to be clamped
        min_value : float
            The minimum value (lower limit)
        max_value : float
            The maximum value (upper limit)

        Returns
        -------
        float
            The clamped value
        """
        return max(min(value, max_value), min_value)

    @staticmethod
    def clamp_01(value: float) -> float:
        """
        Returns a value clamped between 0 and 1

        Parameters
        ----------
        value : float
            The original value to be clamped

        Returns
        -------
        float
            The clamped value
        """
        return Utils.clamp(value, 0.0, 1.0)

    @staticmethod
    def lerp(a: float, b: float, t: float) -> float:
        """
        Linearly interpolates between the points a and b by the interpolant t. The parameter t is clamped to the range [0, 1].

        Use Case
        --------
        When t = 0, returns a

        When t = 1, returns b

        When t = 0.5, returns the midpoint of a and b

        Parameters
        ----------
        a : float
            The start value, returned when t = 0
        b : float
            The start value, returned when t = 1
        t : float
            The value used to interpolate between a and b

        Returns
        -------
        float
            The interpolated float result between the two float values
        """
        t = Utils.clamp_01(t)
        return a + (b - a) * t

    @staticmethod
    def round_rectangle(canvas: Canvas, x1: float, y1: float, x2: float, y2: float, radius: int=25, **kwargs) -> int:
        """
        Creates a rounded rectangle tkinter canvas element with a specified radius

        Source
        ------
        This code was taken from a Stack Overflow answer: https://stackoverflow.com/a/44100075

        Parameters
        ----------
        canvas : Canvas
            The canvas on which to create the rounded rectangle
        x1 : float
            The first or leftmost x coordinate
        y1 : float
            The first or topmost y coordinate
        x2 : float
            The second or rightmost x coordinate
        y2 : float
            The second or bottommost y coordinate
        radius : int
            The radius of the rounded rectangle

        Returns
        -------
        int | _CanvasItemId
            The id of the created canvas item
        """
        points = [x1+radius, y1,
                x1+radius, y1,
                x2-radius, y1,
                x2-radius, y1,
                x2, y1,
                x2, y1+radius,
                x2, y1+radius,
                x2, y2-radius,
                x2, y2-radius,
                x2, y2,
                x2-radius, y2,
                x2-radius, y2,
                x1+radius, y2,
                x1+radius, y2,
                x1, y2,
                x1, y2-radius,
                x1, y2-radius,
                x1, y1+radius,
                x1, y1+radius,
                x1, y1]

        return canvas.create_polygon(points, **kwargs, smooth=True)


class Slider:
    def __init__(self, canvas: Canvas,
        x1: float, y1: float, x2: float, y2: float, radius: int=5,
        bg: str="#838383", fg: str="#DADADA") -> None:
        """
        Parameters
        ----------
        canvas : Canvas
            The canvas on which to create the slider
        x1 : float
            The first or leftmost x coordinate
        y1 : float
            The first or topmost y coordinate
        x2 : float
            The second or rightmost x coordinate
        y2 : float
            The second or bottommost y coordinate
        radius : int
            The radius of the slider
        bg : str
            The background color (The color of the slider background rectangle)
        fg : str
            The foreground color (The color of the moving slider rectangle)

        Returns
        -------
        None
        """
        self.canvas = canvas

        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.start_pos, self.end_pos = x1, x2

        self.radius, self.bg, self.fg = radius, bg, fg

        self.slider_background = Utils.round_rectangle(canvas, x1, y1, x2, y2, radius=radius, fill=bg)
        self.slider_foreground = Utils.round_rectangle(canvas, x1, y1, x1, y2, radius=0, fill=fg)

    def set_position(self, percent: float) -> None:
        """
        Sets the position of the slider based on a percent (decimal form)

        Parameters
        ----------
        percent : float
            The position of the slider

        Returns
        -------
        None
        """
        self.current_pos = Utils.lerp(self.start_pos, self.end_pos, percent)
        self.canvas.delete(self.slider_foreground)
        self.slider_foreground = Utils.round_rectangle(self.canvas, self.x1, self.y1, self.current_pos, self.y2, radius=self.radius, fill=self.fg)


class WebImage:
    def __init__(self, url: str) -> None:
        """
        Parameters
        ----------
        url : str
            The url of the image

        Returns
        -------
        None
        """
        try:
            request = requests.get(url)
            self.image = Image.open(BytesIO(request.content))
            self.photoimage = ImageTk.PhotoImage(self.image)
        except Exception as e:
            self.image, self.photoimage = None, None
            print(f"Could not load image due to an error: {e}")

    def resize(self, size: tuple[int, int]) -> None:
        """
        Resizes the image

        Parameters
        ----------
        size : tuple[int, int]
            The new size of the image

        Returns
        -------
        None
        """
        if not self.image:
            return

        self.image = self.image.resize(size)
        self.photoimage = ImageTk.PhotoImage(self.image)

    def add_corners(self, radius):
        # Source: https://stackoverflow.com/a/11291419
        circle = Image.new('L', (radius * 2, radius * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
        alpha = Image.new('L', self.image.size, 255)
        w, h = self.image.size
        alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
        alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
        alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
        alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
        self.image.putalpha(alpha)

    def get(self) -> PhotoImage:
        """
        Returns the created tkinter PhotoImage

        Returns
        -------
        PhotoImage
            The created tkinter PhotoImage
        """
        return self.photoimage