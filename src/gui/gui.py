"""
The icons used are Google's Material Icons: https://developers.google.com/fonts/docs/material_icons, inserted into
Figma using the Material Design Icons Plugin

Most of the title bar code was derived from these Stack Overflow threads and later modified:
https://stackoverflow.com/questions/23836000/can-i-change-the-title-bar-in-tkinter
https://stackoverflow.com/questions/49621671/trouble-making-a-custom-title-bar-in-tkinter
"""

from ctypes.wintypes import BOOL, HWND, LONG
import ctypes
import inspect
import os
from pathlib import Path
import sys

from typing import Optional

from tkinter import END, WORD, Event, Frame, Label, Scrollbar, Tk, Canvas, Entry, Text, Button, PhotoImage, Toplevel

# Allows importing from parent directory
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from database import Playlist, playlist_manager
import player


# The path to load the assets (images) from
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")

def relative_to_assets(path: str) -> Path:
    """
    Returns the full path for a file in the assets folder

    Parameters
    ----------
    path : str
        The file name or file subpath

    Returns
    -------
    Path
        The full file path
    """
    return ASSETS_PATH / Path(path)

def close_main_window() -> None:
    """
    Closes the current SQL session and then closes the window

    Returns
    -------
    None
    """
    playlist_manager.close_session()
    window.destroy()

fullscreen = False

def toggle_fullscreen(event: Optional[Event]=None) -> None:
    """
    Closes the current SQL session and then closes the window

    Parameters
    ----------
    event : Event, optional
        An event object that gets passed in for binded canvas items

    Returns
    -------
    None
    """
    global fullscreen
    if fullscreen == False:
        window.wm_state('zoomed')
        fullscreen = True
    else:
        window.wm_state('normal')
        fullscreen = False

def minimize_window() -> None:
    """
    Minimizes the window

    Returns
    -------
    None
    """
    window.iconify()

# Creates the root window with a title
window = Tk("Music Player")

# Determines whether or not the GUI should rescale for better resolution (Changes DPI)
HIGH_RES = False

if HIGH_RES:
    # DPI Awareness (Increase Pixels per inch)
    # Update window size to match new resolution
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    window.geometry("1006x673")
else:
    window.geometry("+0+0")
    window.geometry("1008x680")

# Updates the window background color
window.configure(bg = "#202020")

# Change the window flags to allow an overrideredirect window to be shown on the taskbar
# See (https://stackoverflow.com/a/30819099/291641, https://stackoverflow.com/a/2400467/11106801)

GWL_STYLE = -16
GWLP_HWNDPARENT = -8
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000

# Defining types
INT = ctypes.c_int
LONG_PTR = ctypes.c_long

def _errcheck_not_zero(value, func, args):
    """
    Error check callback
    (ctypes library code is undocumented)
    """
    if value == 0:
        raise ctypes.WinError()
    return args

# Defining functions
GetWindowLongPtrW = ctypes.windll.user32.GetWindowLongPtrW
SetWindowLongPtrW = ctypes.windll.user32.SetWindowLongPtrW

GetWindowLongPtrW = ctypes.windll.user32.GetWindowLongPtrW
GetWindowLongPtrW.argtypes = (HWND, INT)
GetWindowLongPtrW.restype = LONG_PTR
GetWindowLongPtrW.errcheck = _errcheck_not_zero

SetWindowLongPtrW = ctypes.windll.user32.SetWindowLongPtrW
SetWindowLongPtrW.argtypes = (HWND, INT, LONG_PTR)
SetWindowLongPtrW.restype = LONG_PTR
SetWindowLongPtrW.errcheck = _errcheck_not_zero

def get_handle(root: Tk) -> int:
    """
    Returns the window's parent

    Parameters
    ----------
    root : Tk
        The root tkinter window

    Returns
    -------
    _NamedFuncPointer
    """
    root.update_idletasks()
    return GetWindowLongPtrW(root.winfo_id(), GWLP_HWNDPARENT)

# Removes the title bar of the window
hwnd = get_handle(window)
style = GetWindowLongPtrW(hwnd, GWL_STYLE)
style &= ~(WS_CAPTION | WS_THICKFRAME)
SetWindowLongPtrW(hwnd, GWL_STYLE, style)

# -----------------------------------------------------------------------

def play_search_track(title: str, cover_art_url: str) -> None:
    """
    Plays a track from the search results

    Parameters
    ----------
    tile : str
        The full track title
    cover_art_url: str
        The url for the album cover art image

    Returns
    -------
    None
    """
    global canvas
    if player.stream:
        player.stream.stop()

    full_title = f"{title} Official Audio"
    player.play_search_track(full_title, cover_art_url)

def genre_search(genre: str, time_period: str = "month", songs: int = 20) -> None:
    """
    Gets top tracks in the specific genre

    Parameters
    ----------
    genre : str
        The genre of the results ("all", "rap", "pop", "rb", "rock", "country")
    time_period : str
        Time period of the results. ("day", "week", "month", or "all_time").
    songs : int
        The number of songs to search (max 50)

    Returns
    -------
    None
    """
    results = player.genre_search(genre, time_period, songs)
    populate_search_results(results.get("chart_items"), result_dict_key="item")

def fuzzy_search(search_entry: Entry) -> None:
    """
    Gets search results from an entry

    Parameters
    ----------
    search_entry : Entry
        The entry box containing the search term

    Returns
    -------
    None
    """

    # Gets the search term from the entry box and does a Genius search
    search_term = search_entry.get()
    results = player.fuzzy_search(search_term)
    populate_search_results(results.get("hits"))

def populate_search_results(results: dict, result_dict_key="result") -> None:
    """
    Populates a list of tracks from genius search results

    results : dict
        A dictionary containing information about the search results

    Returns
    -------
    None
    """
    global scroll_view_canvas, canvas
    global heart_empty_image, album_cover_art_image

    # Resets the scroll view and deletes the previous search result elements
    # Also, resets focus (removes entry box cursor)
    scroll_view_canvas.yview_moveto(0)
    scroll_view_canvas.delete("search_categories_element")
    scroll_view_canvas.delete("search_result_element")
    scroll_view_canvas.focus_set()

    # Creates "Songs" title text
    scroll_view_canvas.create_text(
        247.0+82,
        131.99999999999994,
        anchor="nw",
        text="Songs",
        fill="#FFFFFF",
        font=("RobotoRoman Medium", 16, "bold"),
        tag="search_result_element"
    )

    final_row = 0

    # Loops over the search results and creates a frame containing the information about that track
    for row, result in enumerate(results):
        final_row = row + 1
        objs = list()

        # Creates and places the track frame image
        small_frame_image = PhotoImage(
            file=relative_to_assets("image_48.png"))
        objs.append(scroll_view_canvas.create_image(
            621.0+82,
            195.99999999999994 + (row * 66),
            image=small_frame_image,
            tag="search_result_element"
        ))

        # Creates the cover art image from the obtained url
        cover_art_image = player.create_image(result.get(result_dict_key).get("header_image_thumbnail_url"), (40, 40))
        if not cover_art_image:
            cover_art_image = PhotoImage(
            file=relative_to_assets("image_49.png"))

        objs.append(scroll_view_canvas.create_image(
            276.0+82,
            195.99999999999994 + (row * 66),
            image=cover_art_image,
            tag="search_result_element"
        ))

        # Truncates the title and creates track title text on the canvas
        title = player.Utils.truncate_string(result.get(result_dict_key).get("title"), 30)
        objs.append(scroll_view_canvas.create_text(
            316.0+82,
            184.99999999999994 + (row * 66),
            anchor="nw",
            text=title,
            fill="#FFFFFF",
            font=("RobotoRoman Medium", 12),
            tag="search_result_element"
        ))

        # Truncates the artist name and creates track artist text on the canvas
        artist = player.Utils.truncate_string(result.get(result_dict_key).get("artist_names"), 30)
        objs.append(scroll_view_canvas.create_text(
            590.0+82,
            184.99999999999994 + (row * 66),
            anchor="nw",
            text=artist,
            fill="#FFFFFF",
            font=("RobotoRoman Medium", 12),
            tag="search_result_element"
        ))

        # Creates a heart button image (placeholder)
        heart_button = scroll_view_canvas.create_image(
            960.0+82,
            195.99999999999994 + (row * 66),
            image=heart_empty_image,
            tag="search_result_element"
        )

        # Appends the images to a list stored on the canvas so they won't be automatically garbage collected
        scroll_view_canvas.images.append(small_frame_image)
        scroll_view_canvas.images.append(cover_art_image)

        # Binds the track frame elements to playing the track
        for obj in objs:
            scroll_view_canvas.tag_bind(obj, "<ButtonPress-1>", lambda event, title=result.get(result_dict_key).get("full_title"), cover_art_url=result.get(result_dict_key).get("header_image_thumbnail_url"): play_search_track(title, cover_art_url))

    # Creates a rectangle after the results to allow for more room to scroll
    scroll_view_canvas.create_rectangle(
        300.0,
        180.0 + (final_row * 66.0),
        1106.0,
        190.0 + (final_row * 66.0),
        fill="#202020",
        outline="",
        tag="search_result_element"
    )

    # Configure the canvas scroll region
    onFrameConfigure(scroll_view_canvas)

    # scroll_view_canvas.create_text(
    #     247.0+82,
    #     339.99999999999994,
    #     anchor="nw",
    #     text="YouTube",
    #     fill="#FFFFFF",
    #     font=("RobotoRoman Medium", 16, "bold"),
    #     tag="search_result_element"
    # )

    # large_frame_image = PhotoImage(
    #     file=relative_to_assets("image_50.png"))
    # large_frame = scroll_view_canvas.create_image(
    #     621.0+82,
    #     421.99999999999994,
    #     image=large_frame_image,
    #     tag="search_result_element"
    # )

    # video_thumbnail_image = PhotoImage(
    #     file=relative_to_assets("image_51.png"))
    # video_thumbnail = scroll_view_canvas.create_image(
    #     319.0+82,
    #     420.99999999999994,
    #     image=video_thumbnail_image,
    #     tag="search_result_element"
    # )

    # scroll_view_canvas.create_text(
    #     402.0+82,
    #     419.99999999999994,
    #     anchor="nw",
    #     text="Lea Makhoul",
    #     fill="#FFFFFF",
    #     font=("RobotoRoman Light", 10),
    #     tag="search_result_element"
    # )

    # scroll_view_canvas.create_text(
    #     402.0+82,
    #     400.99999999999994,
    #     anchor="nw",
    #     text="Lea Makhoul - RATATA (Official Music Video) ft. B.O.X",
    #     fill="#FFFFFF",
    #     font=("RobotoRoman Medium", 12),
    #     tag="search_result_element"
    # )

    # scroll_view_canvas.create_text(
    #     931.0+82,
    #     410.99999999999994,
    #     anchor="nw",
    #     text="3:08",
    #     fill="#FFFFFF",
    #     font=("RobotoRoman Light", 10),
    #     tag="search_result_element"
    # )

    # heart_button_2 = scroll_view_canvas.create_image(
    #     895.0+82,
    #     421.99999999999994,
    #     image=heart_empty_image,
    #     tag="search_result_element"
    # )

    # scroll_view_canvas.images.append(large_frame_image)
    # scroll_view_canvas.images.append(video_thumbnail_image)

def cancel_search(canvas: Canvas, canvas_window: int, search_entry: Entry) -> None:
    """
    Clears the search box and removes the search results

    Parameters
    ----------
    canvas : Canvas
        The canvas that contains the entry window
    canvas_window: int
        The canvas window that contains the entry
    search_entry : Entry
        The entry box containing the search term

    Returns
    -------
    None
    """
    
    # Clears the search entry text
    search_entry.delete(0, END)
    check_textbox_content(canvas, canvas_window, search_entry)

    # Resets the scroll view and deletes all canvas elements
    # Also, resets focus (removes entry box cursor)
    scroll_view_canvas.yview_moveto(0)
    scroll_view_canvas.delete("search_result_element")
    scroll_view_canvas.focus_set()

    display_search_categories()

    # Configure the canvas scroll region
    onFrameConfigure(scroll_view_canvas)

def display_search_categories():
    global scroll_view_canvas, canvas
    # Resets the scroll view and deletes all canvas elements
    # Also, resets focus (removes entry box cursor)
    scroll_view_canvas.delete("search_result_element")
    scroll_view_canvas.focus_set()

    # Creates "Categories" title text
    scroll_view_canvas.create_text(
        247.0+82,
        131.99999999999994,
        anchor="nw",
        text="Categories",
        fill="#FFFFFF",
        font=("RobotoRoman Medium", 16, "bold"),
        tag="search_categories_element"
    )

    categories = ["rap", "pop", "rb", "rock", "country", "all"]
    category_images_list = ["image_56.png", "image_57.png", "image_58.png", "image_59.png", "image_60.png", "image_61.png"]
    category_images_rows = player.Utils.split_list(category_images_list, 3)

    index = 0
    for row, category_images in enumerate(category_images_rows):
        for column, category_image in enumerate(category_images):
            category_button_image = PhotoImage(
                file=relative_to_assets(category_image))
            category_button = scroll_view_canvas.create_image(
                444.0 + (column * 259.0),
                233.0 + (row * 154.0),
                image=category_button_image,
                tag="search_categories_element"
            )

            scroll_view_canvas.tag_bind(category_button, "<ButtonPress-1>",
                    lambda event, g=categories[index]: genre_search(g))

            # Appends the images to a list stored on the canvas so they won't be automatically garbage collected
            scroll_view_canvas.images.append(category_button_image)

            index += 1

    top_songs_button_image = PhotoImage(
    file=relative_to_assets("image_62.png"))
    top_songs_button = scroll_view_canvas.create_image(
        703.0,
        541.0,
        image=top_songs_button_image,
        tag="search_categories_element"
    )

    scroll_view_canvas.create_rectangle(
        300.0,
        629.0,
        1106.0,
        639.0,
        fill="#202020",
        outline="",
        tag="search_result_element"
    )

    scroll_view_canvas.tag_bind(top_songs_button, "<ButtonPress-1>",
        lambda event, g="all", t="all_time", s=50: genre_search(g, t, s))
    scroll_view_canvas.images.append(top_songs_button_image)

def search_tab() -> None:
    """
    Deletes all canvas elements for other tabs and creates the search bar for the search tab

    Returns
    -------
    None
    """
    global scroll_view_canvas, canvas

    # Resets the scroll view and deletes all canvas elements
    # Also, resets focus (removes entry box cursor)
    scroll_view_canvas.yview_moveto(0)
    scroll_view_canvas.delete("track_element")
    scroll_view_canvas.delete("playlist_element")
    scroll_view_canvas.delete("search_tab_element")
    scroll_view_canvas.delete("search_result_element")
    scroll_view_canvas.delete("search_categories_element")

    # Creates a list of images on the canvas to append to (to avoid auto garbage collection)
    scroll_view_canvas.images = list()

    # Creates the search bar bg image and places it on the canvas
    search_bar_image = PhotoImage(
    file=relative_to_assets("image_46.png"))
    search_bar = scroll_view_canvas.create_image(
        621.0+82,
        82,
        image=search_bar_image
    )

    # Creates the cancel search button image and places it on the canvas
    cancel_search_button_image = PhotoImage(
        file=relative_to_assets("image_47.png"))
    cancel_search_button = scroll_view_canvas.create_image(
        973.0+82,
        81,
        image=cancel_search_button_image,
        tag="search_tab_element"
    )

    # Creates the search entry and places it in a canvas window
    search_entry = Entry(
        scroll_view_canvas,
        width = 50,
        bg = "#FFFFFF",
        fg = "#303030",
        bd = 0,
        highlightthickness = 0,
        relief = "ridge",
        font = ("RobotoRoman Medium", 12),
        insertbackground = "#303030"
    )
    search_entry_window = scroll_view_canvas.create_window(600, 82, window=search_entry, tag="search_tab_element")
    check_textbox_content(scroll_view_canvas, search_entry_window, search_entry)

    # Configure the canvas scroll region
    onFrameConfigure(scroll_view_canvas)

    # Removes focus from the search bar entry field when the canvas is clicked
    scroll_view_canvas.bind("<ButtonPress-1>", lambda event: scroll_view_canvas.focus_set())

    # Check if the entry filed contains anything before removing it
    search_entry.bind("<FocusOut>", lambda event, c=scroll_view_canvas, w=search_entry_window, e=search_entry: check_textbox_content(c, w, e))
    # Populate the search results upon pressing enter
    search_entry.bind("<Return>", lambda event, e=search_entry: fuzzy_search(e))

    # Creates the entry box to type in when the search bar is clicked
    scroll_view_canvas.tag_bind(search_bar, "<ButtonPress-1>", lambda event, c=scroll_view_canvas, w=search_entry_window, e=search_entry: edit_textbox(c, w, e))
    # Cancel the search when the cancel search button is clicked
    scroll_view_canvas.tag_bind(cancel_search_button, "<ButtonPress-1>", lambda event, c=scroll_view_canvas, w=search_entry_window, e=search_entry: cancel_search(c, w, e))

    # Appends the images to a list stored on the canvas so they won't be automatically garbage collected
    scroll_view_canvas.images.append(search_bar_image)
    scroll_view_canvas.images.append(cancel_search_button_image)

    display_search_categories()

def check_textbox_content(canvas: Canvas, canvas_window: int, text_entry: Entry) -> None:
    """
    Checks whether to hide or show the entry field depending on whether or not there is any content in it

    Parameters
    ----------
    canvas : Canvas
        The canvas that contains the entry window
    canvas_window: int
        The canvas window that contains the entry
    text_entry : Entry
        The text entry

    Returns
    -------
    None
    """
    description_state = "normal"
    if type(text_entry) == Text:
        description_state = "hidden" if not text_entry.get("1.0", END).strip() else "normal"
    elif type(text_entry) == Entry:
        description_state = "hidden" if not text_entry.get() else "normal"

    canvas.itemconfigure(canvas_window, state=description_state)

def edit_textbox(canvas: Canvas, canvas_window: int, text_entry: Entry):
    """
    Creates and shows the text entry and gives focus

    Parameters
    ----------
    canvas : Canvas
        The canvas that contains the entry window
    canvas_window: int
        The canvas window that contains the entry
    text_entry : Entry
        The text entry

    Returns
    -------
    None
    """
    canvas.itemconfigure(canvas_window, state="normal")
    text_entry.focus()

def delete_playlist(overlay_window: Toplevel, playlist: Playlist) -> None:
    """
    Deletes a playlist from the database and repopulates the list of playlists

    Parameters
    ----------
    overlay_window : Toplevel
        The toplevel window containing playlist details
    playlist: Playlist
        The playlist to delete

    Returns
    -------
    None
    """
    playlist_manager.delete_playlist(playlist)
    close_toplevel_window(overlay_window)
    populate_playlists()

def save_playlist_details(overlay_window: Toplevel, playlist: Playlist, title_entry: Entry, description_entry: Entry) -> None:
    """
    Saves the playlist details that were updated in the edit details box

    Parameters
    ----------
    overlay_window : Toplevel
        The toplevel window containing playlist details
    playlist: Playlist
        The playlist to save details to
    title_entry : Entry
        The title entry to retrieve the track title from
    description_entry : Entry
        The title entry to retrieve the track description from

    Returns
    -------
    None
    """
    current_title = playlist.title
    current_description = playlist.description
    new_title = title_entry.get()
    new_description = description_entry.get("1.0", END).strip()

    # Closes the edit details window
    close_toplevel_window(overlay_window)

    # If none of the details have changes, don't save the data
    if current_title == new_title and current_description == new_description:
        return

    # If the title changed and there isn't another playlist with the same title, rename the playlist
    if new_title and current_title != new_title and not playlist_manager.playlist_exists(new_title):
        playlist_manager.rename_playlist(playlist, new_title)
    # If the description changed, update the playlist description
    if current_description != new_description:
        playlist_manager.edit_playlist_description(playlist, new_description)

    # Repopulate the list of tracks
    populate_tracks(playlist)

def close_toplevel_window(window: Toplevel) -> None:
    """
    Destroys the toplevel window

    Parameters
    ----------
    window : Toplevel
        The toplevel window to destroy

    Returns
    -------
    None
    """
    window.destroy()
    window.update()

def create_overlay_window() -> tuple[Toplevel, Canvas]:
    """
    Creates a transparent overlay window with no titlebar and a canvas with a dark background

    Returns
    -------
    tuple[Toplevel, Canvas]
        A tuple of the toplevel window and the canvas that is contained on the window
    """
    global window
    overlay_window = Toplevel(window)
    overlay_window.overrideredirect(True)
    overlay_window.geometry(f"1024x720+{window.winfo_x()}+{window.winfo_y()}")
    overlay_window.wm_attributes("-alpha", 0.65)
    overlay_window.configure(background="#101010")

    overlay_canvas = Canvas(overlay_window, width=1024, height=720, highlightthickness=0)
    overlay_canvas.pack()
    overlay_rectangle = overlay_canvas.create_rectangle(0, 0, 1024, 720, fill="#101010")

    # Binds the rectangle to close the window when clicked
    overlay_canvas.tag_bind(overlay_rectangle, "<ButtonPress-1>", lambda event: close_toplevel_window(overlay_window))

    # Closes the overlay window when the program is minimized (to prevent duplicates and window separation)
    window.bind("<Unmap>", lambda event: close_toplevel_window(overlay_window))

    return overlay_window, overlay_canvas

def create_edit_window() -> tuple[Toplevel, Toplevel, Canvas]:
    """
    Creates an overlay and a toplevel window

    Returns
    -------
    tuple[Toplevel, Toplevel, Canvas]
        A tuple of the overlay window, the edit window and the canvas that is contained on the edit window
    """
    overlay_window, overlay_canvas = create_overlay_window()
    edit_window = Toplevel(overlay_window)
    edit_window.overrideredirect(True)
    edit_window.geometry(f"1024x720+{window.winfo_x()}+{window.winfo_y()}")

    # Makes the window transparent (to allow for rounded corners for the image frame)
    edit_window.config(background="red")
    edit_window.attributes("-transparentcolor", "red")

    # Set the window as topmost to put it on top, then set to False to allow other program windows to be able to be set on top
    edit_window.wm_attributes("-topmost", True)
    edit_window.update()
    edit_window.wm_attributes("-topmost", False)

    # Create a canvas on the edit window
    edit_canvas = Canvas(edit_window, width=1024, height=720, highlightthickness=0, bg="red")
    edit_canvas.pack()

    return overlay_window, edit_window, edit_canvas

def create_rename_window(playlist: Playlist) -> None:
    """
    Creates a toplevel window containing playlist details to edit

    Returns
    -------
    None
    """

    # Creates the edit window and a list of images on the edit canvas (to avoid garbage collection)
    overlay_window, edit_window, edit_canvas = create_edit_window()
    edit_canvas.images = list()

    # Creates the playlist details frame image on the canvas
    playlist_details_box_image = PhotoImage(
    file=relative_to_assets("image_35.png"))
    playlist_details_box = edit_canvas.create_image(
        512.0,
        335.99999999999994,
        image=playlist_details_box_image
    )

    # Creates the title text box image on the canvas
    title_entry_image = PhotoImage(
        file=relative_to_assets("image_36.png"))
    title_textbox = edit_canvas.create_image(
        598.0,
        270.99999999999994,
        image=title_entry_image
    )

    # Creates the title entry on a canvas window
    title_entry = Entry(
        edit_canvas,
        width = 26,
        bg = "#4B4B4B",
        fg = "#FFFFFF",
        bd = 0,
        highlightthickness = 0,
        relief = "ridge",
        font = ("RobotoRoman Medium", 12, "bold"),
        insertbackground = "#FFFFFF"
    )
    # Make the entry contain the current playlist title
    title_entry.insert(END, playlist.title)
    title_entry_window = edit_canvas.create_window(597, 271, window=title_entry)

    # Creates the description text box image on the canvas
    description_entry_image = PhotoImage(
        file=relative_to_assets("image_37.png"))
    description_textbox = edit_canvas.create_image(
        598.0,
        356.99999999999994,
        image=description_entry_image
    )

    # Creates the description entry on a canvas window
    description_entry = Text(
        edit_canvas,
        width = 26,
        height = 5,
        bg = "#4B4B4B",
        fg = "#FFFFFF",
        bd = 0,
        highlightthickness = 0,
        relief = "ridge",
        font = ("RobotoRoman Medium", 12),
        insertbackground = "#FFFFFF",
        wrap = WORD
    )
    # Make the entry contain the current playlist description
    description_entry.insert("1.0", playlist.description)

    description_entry_window = edit_canvas.create_window(597, 356, window=description_entry)
    check_textbox_content(edit_canvas, description_entry_window, description_entry)

    # Creates a preview of the playlist album cover image
    if playlist.title == "Liked Songs":
        playlist_image = PhotoImage(
            file=relative_to_assets("image_41.png"))
    elif playlist.tracks and playlist.tracks[0].cover_art_url:
        playlist_image = player.create_image(playlist.tracks[0].cover_art_url, (160, 160), 15)
    else:
        playlist_image = PhotoImage(
            file=relative_to_assets("image_40.png"))
    edit_canvas.create_image(
        378.0,
        331.99999999999994,
        image=playlist_image
    )

    # Creates the save button image on the canvas
    save_button_image = PhotoImage(
        file=relative_to_assets("image_38.png"))
    save_button = edit_canvas.create_image(
        674.0,
        448.99999999999994,
        image=save_button_image
    )

    # Creates the delete playlist button image on the canvas
    delete_button_image = PhotoImage(
    file=relative_to_assets("image_45.png"))
    delete_button = edit_canvas.create_image(
        557.0,
        448.99999999999994,
        image=delete_button_image
    )

    # Creates the close window button image on the canvas
    close_button_image = PhotoImage(
        file=relative_to_assets("image_39.png"))
    close_button = edit_canvas.create_image(
        720.0,
        215.99999999999994,
        image=close_button_image
    )


    # Create the entry fields when the text box images are clicked
    edit_canvas.tag_bind(description_textbox, "<ButtonPress-1>", lambda event, c=edit_canvas, w=description_entry_window, e=description_entry: edit_textbox(c, w, e))
    edit_canvas.tag_bind(title_textbox, "<ButtonPress-1>", lambda event, c=edit_canvas, w=title_entry_window, e=title_entry: edit_textbox(c, w, e))

    # Remove focus from the text entries when the details box is clicked
    edit_canvas.tag_bind(playlist_details_box, "<ButtonPress-1>", lambda event: edit_canvas.focus_set())

    # Check if the entries can be removed if empty when they lose focus
    description_entry.bind("<FocusOut>", lambda event, c=edit_canvas, w=description_entry_window, e=description_entry: check_textbox_content(c, w, e))
    title_entry.bind("<FocusOut>", lambda event, c=edit_canvas, w=title_entry_window, e=title_entry: check_textbox_content(c, w, e))

    # Binds the title and description entries enter to save the new playlist details
    title_entry.bind("<Return>", lambda event, w=overlay_window, p=playlist, t=title_entry, d=description_entry: save_playlist_details(w, p, t, d))
    description_entry.bind("<Return>", lambda event, w=overlay_window, p=playlist, t=title_entry, d=description_entry: save_playlist_details(w, p, t, d))

    # Binds the delete, save, and close buttons
    edit_canvas.tag_bind(delete_button, "<ButtonPress-1>", lambda event, w=overlay_window, p=playlist: delete_playlist(w, p))
    edit_canvas.tag_bind(save_button, "<ButtonPress-1>", lambda event, w=overlay_window, p=playlist, t=title_entry, d=description_entry: save_playlist_details(w, p, t, d))
    edit_canvas.tag_bind(close_button, "<ButtonPress-1>", lambda event: close_toplevel_window(overlay_window))

    # Appends the images to a list stored on the canvas so they won't be automatically garbage collected
    edit_canvas.images.append(playlist_details_box_image)
    edit_canvas.images.append(title_entry_image)
    edit_canvas.images.append(description_entry_image)
    edit_canvas.images.append(playlist_image)
    edit_canvas.images.append(save_button_image)
    edit_canvas.images.append(delete_button_image)
    edit_canvas.images.append(close_button_image)

def toggle_edit_details_popup(playlist_title: int, hidden: bool=False) -> None:
    """
    Show/hide the edit details pen icon when the playlist name is hovered over

    Parameters
    ----------
    playlist_title : int
        The playlist title canvas item
    hidden : bool
        Whether the icon should be hidden or not

    Returns
    -------
    None
    """
    global scroll_view_canvas
    state = "hidden" if hidden else "normal"
    scroll_view_canvas.itemconfigure(playlist_title, state=state)

def add_track_manually(overlay_window: Toplevel, link_entry: Entry, playlist_entry: Entry) -> None:
    """
    Add the specified track, podcast, or playlist url to the specified playlist

    Parameters
    ----------
    overlay_window : Toplevel
        The toplevel window containing the add track manual window
    link_entry : Entry
        The link entry to retrieve the URL from
    playlist_entry : Entry
        The playlist entry to retrieve the playlist name from

    Returns
    -------
    None
    """
    url = link_entry.get()
    playlist_name = playlist_entry.get()

    if not playlist_name:
        playlist_name = "Liked Songs"

    # Closes the edit details window
    close_toplevel_window(overlay_window)

    player.add_track_manually(url, playlist_name)

    # Repopulate the list of playlists
    populate_playlists()

def create_add_track_window() -> None:
    """
    Creates a toplevel window containing an entry to add a track, playlist, or podcast via url

    Returns
    -------
    None
    """

    # Creates the edit window and a list of images on the edit canvas (to avoid garbage collection)
    overlay_window, edit_window, edit_canvas = create_edit_window()
    edit_canvas.images = list()

    # Creates the add tracks frame image on the canvas
    add_tracks_box_image = PhotoImage(
    file=relative_to_assets("image_52.png"))
    add_tracks_box = edit_canvas.create_image(
        512.0,
        358.99999999999994,
        image=add_tracks_box_image
    )

    # Creates the link text box image on the canvas
    link_entry_image = PhotoImage(
        file=relative_to_assets("image_54.png"))
    link_textbox = edit_canvas.create_image(
        512.0,
        326.99999999999994,
        image=link_entry_image
    )

    # Creates the link entry on a canvas window
    link_entry = Entry(
        edit_canvas,
        width = 45,
        bg = "#4B4B4B",
        fg = "#FFFFFF",
        bd = 0,
        highlightthickness = 0,
        relief = "ridge",
        font = ("RobotoRoman Medium", 12),
        insertbackground = "#FFFFFF"
    )
    link_entry_window = edit_canvas.create_window(511, 327, window=link_entry)
    check_textbox_content(edit_canvas, link_entry_window, link_entry)

    # Creates the playlist text box image on the canvas
    playlist_entry_image = PhotoImage(
        file=relative_to_assets("image_53.png"))
    playlist_textbox = edit_canvas.create_image(
        512.0,
        375.99999999999994,
        image=playlist_entry_image
    )

    # Creates the link entry on a canvas window
    playlist_entry = Entry(
        edit_canvas,
        width = 45,
        bg = "#4B4B4B",
        fg = "#FFFFFF",
        bd = 0,
        highlightthickness = 0,
        relief = "ridge",
        font = ("RobotoRoman Medium", 12, "bold"),
        insertbackground = "#FFFFFF"
    )
    playlist_entry_window = edit_canvas.create_window(511, 376, window=playlist_entry)
    check_textbox_content(edit_canvas, playlist_entry_window, playlist_entry)

    # Creates the add button image on the canvas
    add_button_image = PhotoImage(
        file=relative_to_assets("image_55.png"))
    add_button = edit_canvas.create_image(
        674.0,
        438.99999999999994,
        image=add_button_image
    )

    # Creates the close window button image on the canvas
    close_button_image = PhotoImage(
        file=relative_to_assets("image_39.png"))
    close_button = edit_canvas.create_image(
        720.0,
        271.99999999999994,
        image=close_button_image
    )


    # Create the entry fields when the text box images are clicked
    edit_canvas.tag_bind(link_textbox, "<ButtonPress-1>", lambda event, c=edit_canvas, w=link_entry_window, e=link_entry: edit_textbox(c, w, e))
    edit_canvas.tag_bind(playlist_textbox, "<ButtonPress-1>", lambda event, c=edit_canvas, w=playlist_entry_window, e=playlist_entry: edit_textbox(c, w, e))

    # Remove focus from the text entries when the details box is clicked
    edit_canvas.tag_bind(add_tracks_box, "<ButtonPress-1>", lambda event: edit_canvas.focus_set())

    # Check if the entries can be removed if empty when they lose focus
    link_entry.bind("<FocusOut>", lambda event, c=edit_canvas, w=link_entry_window, e=link_entry: check_textbox_content(c, w, e))
    playlist_entry.bind("<FocusOut>", lambda event, c=edit_canvas, w=playlist_entry_window, e=playlist_entry: check_textbox_content(c, w, e))

    # Binds the title and description entries enter to save the new playlist details
    # title_entry.bind("<Return>", lambda event, w=overlay_window, p=playlist, t=title_entry, d=description_entry: save_playlist_details(w, p, t, d))

    # Binds the add and close buttons
    edit_canvas.tag_bind(add_button, "<ButtonPress-1>", lambda event, w=overlay_window, l=link_entry, p=playlist_entry: add_track_manually(w, l, p))
    edit_canvas.tag_bind(close_button, "<ButtonPress-1>", lambda event: close_toplevel_window(overlay_window))

    # Appends the images to a list stored on the canvas so they won't be automatically garbage collected
    edit_canvas.images.append(add_tracks_box_image)
    edit_canvas.images.append(link_entry_image)
    edit_canvas.images.append(playlist_entry_image)
    edit_canvas.images.append(add_button_image)
    edit_canvas.images.append(close_button_image)

def populate_tracks(playlist: Playlist) -> None:
    """
    Populate the list of tracks in a specific playlist along with the general playlist details (cover image, length, duration)

    Parameters
    ----------
    playlist : Playlist
        The playlist from which to populate the tracks

    Returns
    -------
    None
    """
    global scroll_view_canvas, canvas, track_title_text, track_artist_text
    global heart_button, heart_empty_image, heart_full_image
    global play_button, pause_button_image, play_button_image
    global total_time_text
    global search_entry

    # Resets the scroll view and deletes all canvas elements
    # Also, resets focus (removes entry box cursor)
    scroll_view_canvas.yview_moveto(0)
    scroll_view_canvas.delete("track_element")
    scroll_view_canvas.delete("playlist_element")
    scroll_view_canvas.delete("search_tab_element")
    scroll_view_canvas.delete("search_result_element")
    scroll_view_canvas.delete("search_categories_element")

    if search_entry:
        search_entry.delete()

    # Creates the playlist details background rectangle on the scroll canvas
    scroll_view_canvas.create_rectangle(
        300.0,
        33.0,
        1106.0,
        241.0,
        fill="#292929",
        outline="",
        tag="track_element"
    )

    # Creates the playlist cover image preview
    if playlist.title == "Liked Songs":
        playlist_image = PhotoImage(
            file=relative_to_assets("image_41.png"))
    elif playlist.tracks and playlist.tracks[0].cover_art_url:
        playlist_image = player.create_image(playlist.tracks[0].cover_art_url, (160, 160), 15)
    else:
        playlist_image = PhotoImage(
            file=relative_to_assets("image_40.png"))

    playlist_cover_art = scroll_view_canvas.create_image(
        326.0+82,
        135.99999999999994,
        image=playlist_image,
        tag="track_element"
    )

    # Truncates the playlist title and creates the text on the canvas
    playlist_title_name = player.Utils.truncate_string(playlist.title, 20)
    playlist_title = scroll_view_canvas.create_text(
        432.0+82,
        85.0,
        anchor="nw",
        text=playlist_title_name,
        fill="#FFFFFF",
        font=("RobotoRoman Medium", 32, "bold"),
        tag="track_element"
    )

    title_text_bounds = scroll_view_canvas.bbox(playlist_title)

    # Creates the edit details icon popup depending on the length of the title
    edit_details_image = PhotoImage(
    file=relative_to_assets("image_42.png"))
    edit_details_popup = scroll_view_canvas.create_image(
        title_text_bounds[2] + 25.0,
        113.0,
        image=edit_details_image,
        state = "hidden"
    )

    # Add bindings to edit the playlist details for all playlists except "Liked Songs"
    if playlist.title != "Liked Songs":
        scroll_view_canvas.tag_bind(playlist_title, "<Enter>", lambda event: toggle_edit_details_popup(edit_details_popup, False))
        scroll_view_canvas.tag_bind(playlist_title, "<Leave>", lambda event: toggle_edit_details_popup(edit_details_popup, True))
        scroll_view_canvas.tag_bind(playlist_title, "<ButtonPress-1>", lambda event, playlist=playlist: create_rename_window(playlist))
        scroll_view_canvas.tag_bind(playlist_cover_art, "<ButtonPress-1>", lambda event, playlist=playlist: create_rename_window(playlist))

    # Create playlist author text on the canvas
    scroll_view_canvas.create_text(
        433.0+82,
        135.0,
        anchor="nw",
        text="Ryan",
        fill="#FFFFFF",
        font=("RobotoRoman Light", 14),
        tag="track_element"
    )

    # Get information about the playlist (length and duration) and create text on the canvas to display the info
    playlist_information = player.get_playlist_info(playlist)

    scroll_view_canvas.create_text(
        433.0+82,
        165.0,
        anchor="nw",
        text=playlist_information,
        fill="#BBBBBB",
        font=("RobotoRoman Light", 12),
        tag="track_element"
    )

    # Create the playlist play/pause button image on the canvas
    play_image = PhotoImage(
        file=relative_to_assets("image_32.png"))

    pause_image = PhotoImage(
        file=relative_to_assets("image_33.png"))

    scroll_view_canvas.create_image(
        885.0+82,
        170.0,
        image=play_image,
        tag="track_element"
    )

    # Create the playlist shuffle tracks button image on the canvas
    shuffle_image = PhotoImage(
        file=relative_to_assets("image_34.png"))
    scroll_view_canvas.create_image(
        935.0+82,
        170.0,
        image=shuffle_image,
        tag="track_element"
    )

    # Create the playlist download toggle local/streaming button image on the canvas
    download_image = PhotoImage(
        file=relative_to_assets("image_43.png"))

    downloaded_image = PhotoImage(
        file=relative_to_assets("image_44.png"))

    scroll_view_canvas.create_image(
        975.0+82,
        170.0,
        image=download_image,
        tag="track_element"
    )

    # Create the the track number header text on the canvas
    scroll_view_canvas.create_text(
        270.0+82,
        265.99999999999994,
        anchor="nw",
        text="#",
        fill="#FFFFFF",
        font=("RobotoRoman Light", 12),
        tag="track_element"
    )

    # Create the the track title header text on the canvas
    scroll_view_canvas.create_text(
        331.0+82,
        265.99999999999994,
        anchor="nw",
        text="Title",
        fill="#FFFFFF",
        font=("RobotoRoman Light", 12),
        tag="track_element"
    )

    # Create the the track artist header text on the canvas
    scroll_view_canvas.create_text(
        496.0+82,
        265.99999999999994,
        anchor="nw",
        text="Artist",
        fill="#FFFFFF",
        font=("RobotoRoman Light", 12),
        tag="track_element"
    )

    # Create the the track album header text on the canvas
    scroll_view_canvas.create_text(
        645.0+82,
        265.99999999999994,
        anchor="nw",
        text="Album",
        fill="#FFFFFF",
        font=("RobotoRoman Light", 12),
        tag="track_element"
    )

    # Create the the track date added header text on the canvas
    scroll_view_canvas.create_text(
        791.0+82,
        265.99999999999994,
        anchor="nw",
        text="Date Added",
        fill="#FFFFFF",
        font=("RobotoRoman Light", 12),
        tag="track_element"
    )

    # Create the the track duration header image on the canvas
    duration_image = PhotoImage(
        file=relative_to_assets("image_29.png"))
    scroll_view_canvas.create_image(
        948.0+82,
        273.99999999999994,
        image=duration_image,
        tag="track_element"
    )

    # Create the the header separator rectangle on the canvas
    scroll_view_canvas.create_rectangle(
        246.0+82,
        292.99999999999994,
        996.0+82,
        293.99999999999994,
        fill="#5B5B5B",
        outline="",
        tag="track_element"
    )

    final_row = 0

    for row, track in enumerate(playlist.tracks):
        # Iterate over the list of tracks in the playlist

        final_row = row + 1
        objs = list()

        # Create the track frame image
        track_frame_image = PhotoImage(
            file=relative_to_assets("image_30.png"))
        objs.append(scroll_view_canvas.create_image(
            621.0+82,
            324.99999999999994 + (row * 52),
            image=track_frame_image,
            tag="track_element"
        ))

        # Create the track number text
        objs.append(scroll_view_canvas.create_text(
            270.0+82,
            314.99999999999994 + (row * 52),
            anchor="nw",
            text=str(row+1),
            fill="#FFFFFF",
            font=("RobotoRoman Medium", 12),
            tag="track_element"
        ))

        # Truncate the track title and Create the track title text on the canvas
        track_title = player.Utils.truncate_string(track.title, 18)
        objs.append(scroll_view_canvas.create_text(
            331.0+82,
            314.99999999999994 + (row * 52),
            anchor="nw",
            text=track_title,
            fill="#FFFFFF",
            font=("RobotoRoman Medium", 12),
            tag="track_element"
        ))

        # Truncate the track artist and Create the track artist text on the canvas
        track_artist = player.Utils.truncate_string(track.artist, 16)
        objs.append(scroll_view_canvas.create_text(
            496.0+82,
            314.99999999999994 + (row * 52),
            anchor="nw",
            text=track_artist,
            fill="#FFFFFF",
            font=("RobotoRoman Medium", 12),
            tag="track_element"
        ))

        # Truncate the track album and Create the track album text on the canvas
        track_album = player.Utils.truncate_string(track.album, 16)
        objs.append(scroll_view_canvas.create_text(
            645.0+82,
            314.99999999999994 + (row * 52),
            anchor="nw",
            text=track_album,
            fill="#FFFFFF",
            font=("RobotoRoman Medium", 12),
            tag="track_element"
        ))

        # Create the track date added text on the canvas (placeholder)
        objs.append(scroll_view_canvas.create_text(
            791.0+82,
            315.99999999999994 + (row * 52),
            anchor="nw",
            text="2018-12-04",
            fill="#CCCCCC",
            font=("RobotoRoman Light", 11),
            tag="track_element"
        ))

        # Format the track duration in (m:ss) format and create the track duration text on the canvas
        track_duration = player.Utils.get_formatted_time(track.duration)
        objs.append(scroll_view_canvas.create_text(
            947.0+82,
            314.99999999999994 + (row * 52),
            anchor="n",
            text=track_duration,
            fill="#CCCCCC",
            font=("RobotoRoman Light", 11),
            tag="track_element"
        ))

        # Appends the images to a list stored on the canvas so they won't be automatically garbage collected
        scroll_view_canvas.images.append(track_frame_image)

        # Binds the track frame elements to playing the track
        for obj in objs:
            scroll_view_canvas.tag_bind(obj, "<ButtonPress-1>",
                lambda event, track_id=track.id: player.play_database_track(track_id)
            )

    # Creates a rectangle after the tracks to allow for more room to scroll
    scroll_view_canvas.create_rectangle(
        300.0,
        330.0 + (final_row * 52.0),
        1106.0,
        340.0 + (final_row * 52.0),
        fill="#202020",
        outline="",
        tag="track_element"
    )

    # Appends the images to a list stored on the canvas so they won't be automatically garbage collected
    scroll_view_canvas.images.append(playlist_image)
    scroll_view_canvas.images.append(edit_details_image)
    scroll_view_canvas.images.append(play_image)
    scroll_view_canvas.images.append(pause_image)
    scroll_view_canvas.images.append(shuffle_image)
    scroll_view_canvas.images.append(download_image)
    scroll_view_canvas.images.append(downloaded_image)
    scroll_view_canvas.images.append(duration_image)

    # Configure the canvas scroll region
    onFrameConfigure(scroll_view_canvas)

def populate_playlists() -> None:
    """
    Populate the list of playlists in the database

    Returns
    -------
    None
    """
    global scroll_view_canvas, canvas, search_entry

    # Resets the scroll view and deletes all canvas elements
    # Also, resets focus (removes entry box cursor)
    scroll_view_canvas.yview_moveto(0)
    scroll_view_canvas.delete("track_element")
    scroll_view_canvas.delete("playlist_element")
    scroll_view_canvas.delete("search_tab_element")
    scroll_view_canvas.delete("search_result_element")
    scroll_view_canvas.delete("search_categories_element")

    if search_entry:
        search_entry.delete()

    # Creates a list of images on the canvas (to avoid garbarge collection)
    scroll_view_canvas.images = list()

    # Split the list of playlists into sublists for easier organization
    # List the playlists as only 3 per row
    playlist_rows = player.Utils.split_list(playlist_manager.session.query(Playlist).all(), 3)

    for row, playlists in enumerate(playlist_rows):
        for column, playlist in enumerate(playlists):
            # Iterate over the rows and columns in the playlist_rows list and its sublists

            objs = list()

            # Create the playlist frame image on the canvas
            frame_image = PhotoImage(
                file=relative_to_assets("image_25.png"))
            objs.append(scroll_view_canvas.create_image(
                418.0 + (column * 208),
                177.99999999999994 + (row * 260),
                image=frame_image,
                tag="playlist_element"
            ))

            # Truncate the playlist title and create the playlist title text on the canvas
            playlist_title = player.Utils.truncate_string(playlist.title, 18)
            objs.append(scroll_view_canvas.create_text(
                352.0 + (column * 208),
                230.99999999999994 + (row * 260),
                anchor="nw",
                text=playlist_title,
                fill="#FFFFFF",
                font=("RobotoRoman Medium", 11, "bold"),
                tag="playlist_element"
            ))

            # Create the playlist author text on the canvas
            objs.append(scroll_view_canvas.create_text(
                352.0 + (column * 208),
                254.99999999999994 + (row * 260),
                anchor="nw",
                text="Ryan",
                fill="#DDDDDD",
                font=("RobotoRoman Light", 10),
                tag="playlist_element"
            ))

            # Create the playlist cover art on the canvas
            if playlist.title == "Liked Songs":
                playlist_image = PhotoImage(
                    file=relative_to_assets("image_27.png"))
            elif playlist.tracks and playlist.tracks[0].cover_art_url:
                playlist_image = player.create_image(playlist.tracks[0].cover_art_url, (140, 140), 15)
            else:
                playlist_image = PhotoImage(
                    file=relative_to_assets("image_26.png"))

            objs.append(scroll_view_canvas.create_image(
                418.0 + (column * 208),
                149.99999999999994 + (row * 260),
                image=playlist_image,
                tag="playlist_element"
            ))

            # Appends the images to a list stored on the canvas so they won't be automatically garbage collected
            scroll_view_canvas.images.append(frame_image)
            scroll_view_canvas.images.append(playlist_image)

            # Binds the playlist frame elements to populating the tracks in the playlist
            for obj in objs:
                scroll_view_canvas.tag_bind(obj, "<ButtonPress-1>",
                    lambda event, playlist=playlist: populate_tracks(playlist))

    # COnfigure the canvas scroll region
    onFrameConfigure(scroll_view_canvas)

def create_new_playlist() -> None:
    """
    Creates a new playlist and repopulates the list of playlists

    Returns
    -------
    None
    """
    global scroll_view_canvas, canvas

    playlist_created = False
    index = 0
    while not playlist_created:
        playlist_name = f"New Playlist ({index})"
        if not playlist_manager.playlist_exists(playlist_name):
            new_playlist = playlist_manager.get_or_create_playlist(playlist_name)
            playlist_created = True
        index += 1

    populate_tracks(new_playlist)

def view_liked_songs() -> None:
    """
    Populates the list of tracks in the "Liked Songs" playlist

    Returns
    -------
    None
    """
    liked_songs_playlist = playlist_manager.get_or_create_playlist("Liked Songs")
    populate_tracks(liked_songs_playlist)

def onFrameConfigure(canvas: Canvas) -> None:
    """
    Reset the scroll region to encompass the inner frame

    Parameters
    ----------
    canvas : Canvas
        The canvas to configure the scrollregion on

    Returns
    -------
    None
    """
    canvas.configure(scrollregion=canvas.bbox("all"))

def bound_to_mousewheel(event: Event) -> None:
    """
    Binds the mousewheel to scroll the scroll view canvas

    Parameters
    ----------
    event: Event
        Callback parameter containing information about the event

    Returns
    -------
    None
    """
    global scroll_view_canvas
    scroll_view_canvas.bind_all("<MouseWheel>", on_mousewheel)

def unbound_to_mousewheel(event: Event) -> None:
    """
    Unbinds the mousewheel from the scroll view canvas

    Parameters
    ----------
    event: Event
        Callback parameter containing information about the event

    Returns
    -------
    None
    """
    global scroll_view_canvas
    scroll_view_canvas.unbind_all("<MouseWheel>")

def on_mousewheel(event: Event) -> None:
    """
    Scrolls the canvas.
    This code was modified using this source: https://stackoverflow.com/a/37861801

    Parameters
    ----------
    event: Event
        Callback parameter containing information about the event

    Returns
    -------
    None
    """
    global scroll_view_canvas
    scroll_view_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

def mute(mute: bool) -> None:
    global volume_indicator, low_volume_image, medium_volume_image, high_volume_image, mute_volume_image
    if not player.stream or not player.stream.player:
        return
    
    # if player.stream.player.audio_get_volume() <= 33:
    #     unmute_volume_image = low_volume_image
    # elif player.stream.player.audio_get_volume() <= 67:
    #     unmute_volume_image = medium_volume_image
    # else:
    #     unmute_volume_image = high_volume_image

    if mute:
        player.stream.player.audio_set_mute(True)
        canvas.itemconfig(volume_indicator, image=mute_volume_image)
    else:
        player.stream.player.audio_set_mute(False)
        canvas.itemconfig(volume_indicator, image=high_volume_image)

def toggle_mute() -> None:
    """
    Toggles mute for playback andupdates the volume indicator

    Returns
    -------
    None
    """
    global volume_slider
    if not player.stream or not player.stream.player:
        return
    if player.stream.player.audio_get_mute():
        mute(False)
        volume_slider.set_position(player.stream.player.audio_get_volume() / 100)
    else:
        mute(True)
        volume_slider.set_position(0)

def set_volume(percent: float) -> None:
    player.set_volume(percent)

    if percent <= 0:
        mute(True)
    else:
        mute(False)

# Creates the main canvas
canvas = Canvas(
    window,
    bg = "#202020",
    height = 720,
    width = 1024,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)
canvas.place(x = 0, y = 0)

# Creates the main background rectangle
canvas.create_rectangle(
    218.0,
    0.0,
    1024.0,
    640.0,
    fill="#202020",
    outline=""
)

# Creates the scroll view canvas containing the tab content
scroll_view_canvas = Canvas(
    window,
    borderwidth=0,
    background="#202020",
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)
scroll_view_canvas.place(x=218.0, y=33.0, width=806.0, height=607.0)

# Creates the scroll view frame to allow for scrolling
frame = Frame(scroll_view_canvas, background="#202020", width=806.0, padx=20.0, pady=20.0)

scroll_view_canvas.create_window(
    (300,33),
    window=frame,
    anchor="nw"
)

# Bind entering and leaving the scroll view canvas to activating/deactivating scroll
scroll_view_canvas.bind('<Enter>', bound_to_mousewheel)
scroll_view_canvas.bind('<Leave>', unbound_to_mousewheel)

# Configure the canvas scroll region
frame.bind("<Configure>", lambda event, canvas=scroll_view_canvas: onFrameConfigure(scroll_view_canvas))

# Creates the background rectangle for the current playing track playback info
canvas.create_rectangle(
    0.0,
    640.0,
    1024.0,
    720.0,
    fill="#303030",
    outline=""
)

def start_move(event: Event) -> None:
    """
    Start moving the window (toolbar binding callback)

    Parameters
    ----------
    event: Event
        Callback parameter containing information about the event

    Returns
    -------
    None
    """
    global x, y
    window.geometry("1024x720")
    window.wm_overrideredirect(True)
    x = event.x
    y = event.y

def stop_move(event):
    """
    Stop moving the window (toolbar binding callback)

    Parameters
    ----------
    event: Event
        Callback parameter containing information about the event

    Returns
    -------
    None
    """
    global x, y
    if HIGH_RES:
        window.geometry("1006x673")
    else:
        window.geometry("1008x680")
    window.wm_overrideredirect(False)
    hwnd = get_handle(window)
    style = GetWindowLongPtrW(hwnd, GWL_STYLE)
    style &= ~(WS_CAPTION | WS_THICKFRAME)
    SetWindowLongPtrW(hwnd, GWL_STYLE, style)
    x = None
    y = None

def do_move(event):
    """
    Move the window (toolbar binding callback)

    Parameters
    ----------
    event: Event
        Callback parameter containing information about the event

    Returns
    -------
    None
    """
    global x, y

    if x and y:
        window.geometry(f'+{event.x_root - x}+{event.y_root - y}')

# Creates the title bar frame rectangle on the canvas
title_bar_frame = canvas.create_rectangle(
    0.0,
    0.0,
    1024.0,
    33.0,
    fill="#313131",
    outline=""
)

search_entry = None

# Add title bar bindings
canvas.tag_bind(title_bar_frame, "<ButtonPress-1>", start_move)
canvas.tag_bind(title_bar_frame, "<ButtonRelease-1>", stop_move)
canvas.tag_bind(title_bar_frame, "<B1-Motion>", do_move)
canvas.tag_bind(title_bar_frame, '<Double-1>', toggle_fullscreen)

# Open a new databse session
playlist_manager.open_session()

# Populate a list of playlists when the app is opened
populate_playlists()


"""
---------------------------------------------------------------------------------------------------------
A lot of the basic GUI code below was generated using Tkinter Designer: https://github.com/ParthJadhav/Tkinter-Designer,
and was later modified to fit the specific needs of the application
---------------------------------------------------------------------------------------------------------
"""

# Creates the current track play button image and binds it to playing/pausing the current track
play_button_image = PhotoImage(
    file=relative_to_assets("image_1.png"))

pause_button_image = PhotoImage(
    file=relative_to_assets("image_2.png"))

play_button = canvas.create_image(
    511.0,
    669.0,
    image=play_button_image
)

canvas.tag_bind(play_button, "<ButtonPress-1>", lambda event: player.play_pause_track())

# Creates the next track button image and places it on the canvas
next_track_button_image = PhotoImage(
    file=relative_to_assets("image_3.png"))
next_track_button = canvas.create_image(
    561.0,
    671.0,
    image=next_track_button_image
)

# Creates the previous track button image and places it on the canvas
previous_track_button_image = PhotoImage(
    file=relative_to_assets("image_4.png"))
previous_track_button = canvas.create_image(
    460.0,
    671.0,
    image=previous_track_button_image
)

# Creates the current track skip backwards button image and binds it to skipping backwards in playback
skip_backwards_button_image = PhotoImage(
    file=relative_to_assets("image_5.png"))
skip_backwards_button = canvas.create_image(
    416.0,
    670.0,
    image=skip_backwards_button_image
)

canvas.tag_bind(skip_backwards_button, "<ButtonPress-1>", lambda event: player.skip_backwards())

# Creates the current track skip forwards button image and binds it to skipping forwards in playback
skip_forwards_button_image = PhotoImage(
    file=relative_to_assets("image_6.png"))
skip_forwards_button = canvas.create_image(
    602.0,
    670.0,
    image=skip_forwards_button_image
)

canvas.tag_bind(skip_forwards_button, "<ButtonPress-1>", lambda event: player.skip_forwards())

# Creates the track shuffle button image and places it on the canvas
track_shuffle_button_image = PhotoImage(
    file=relative_to_assets("image_7.png"))
track_shuffle_button = canvas.create_image(
    375.0,
    671.0,
    image=track_shuffle_button_image
)

# Creates the current track loop button image and binds it to toggling loop playback
no_loop_button_image = PhotoImage(
    file=relative_to_assets("image_8.png"))

loop_button_image = PhotoImage(
    file=relative_to_assets("image_9.png"))

loop_button = canvas.create_image(
    644.0,
    671.0,
    image=no_loop_button_image
)

canvas.tag_bind(loop_button, "<ButtonPress-1>", lambda event: player.toggle_loop())

# Creates the current track elapsed time slider and places it on the canvas
track_slider = player.Slider(window, canvas, 317.0, 699.0, 707.0, 704.0, callback=player.set_position)

# Creates the current track elapsed time text and places it on the canvas (placeholder - gets reassigned later)
elapsed_time_text = canvas.create_text(
    310.0,
    694.0,
    anchor="ne",
    text="0:00",
    fill="#FFFFFF",
    font=("RobotoRoman Light", 9)
)

# Creates the current track total duration text and places it on the canvas (placeholder - gets reassigned later)
total_time_text = canvas.create_text(
    715.0,
    694.0,
    anchor="nw",
    text="0:00",
    fill="#FFFFFF",
    font=("RobotoRoman Light", 9)
)

# Creates the album cover art placeholder and places it on the canvas (gets reassigned later)
album_cover_art_image = PhotoImage(
    file=relative_to_assets("image_12.png"))
album_cover_art = canvas.create_image(
    43.0,
    681.0,
    image=album_cover_art_image
)

# Creates the current track artist text and places it on the canvas (placeholder - gets reassigned later)
track_artist_text = canvas.create_text(
    85.0,
    683.0,
    anchor="nw",
    text="Post Malone",
    fill="#DDDDDD",
    font=("RobotoRoman Light", 10)
)

# Creates the current track title text and places it on the canvas (placeholder - gets reassigned later)
track_title_text = canvas.create_text(
    85.0,
    663.0,
    anchor="nw",
    text="Congratulations",
    fill="#FFFFFF",
    font=("RobotoRoman Medium", 12, "bold")
)

# Creates the heart/like song button image and places it on the canvas
heart_empty_image = PhotoImage(
    file=relative_to_assets("image_13.png"))

heart_full_image = PhotoImage(
    file=relative_to_assets("image_14.png"))

heart_button = canvas.create_image(
    235.0,
    684.0,
    image=heart_empty_image
)

# Creates the fullscreen preview button image
image_image_15 = PhotoImage(
    file=relative_to_assets("image_15.png"))
image_15 = canvas.create_image(
    796.0,
    678.0,
    image=image_image_15
)

# Creates the lyrics button image
image_image_16 = PhotoImage(
    file=relative_to_assets("image_16.png"))
image_16 = canvas.create_image(
    829.0,
    678.0,
    image=image_image_16
)

# Creates the volume indicator icon/button and binds it to toggling mute
low_volume_image = PhotoImage(
    file=relative_to_assets("image_17.png"))

medium_volume_image = PhotoImage(
    file=relative_to_assets("image_18.png"))

high_volume_image = PhotoImage(
    file=relative_to_assets("image_19.png"))

mute_volume_image = PhotoImage(
    file=relative_to_assets("image_20.png"))

volume_indicator = canvas.create_image(
    861.0,
    677.0,
    image=high_volume_image
)

canvas.tag_bind(volume_indicator, "<ButtonPress-1>", lambda event: toggle_mute())

# Creates the volume slider
volume_slider = player.Slider(window, canvas, 880.0, 675.0, 992.0, 680.0, callback=set_volume)

# Creates the side bar canvas rectangle
canvas.create_rectangle(
    0.0,
    0.0,
    218.0,
    640.0,
    fill="#009CDF",
    outline=""
)

# Creates the "Liked Songs" button and places it on the canvas
liked_songs_button_image = PhotoImage(
    file=relative_to_assets("button_1.png"))
liked_songs_button = Button(
    image=liked_songs_button_image,
    borderwidth=0,
    highlightthickness=0,
    command=view_liked_songs,
    relief="flat"
)
liked_songs_button.place(
    x=0.0,
    y=293.99999999999994,
    width=218.0,
    height=43.0
)

# Creates the "Create Playlist" button and places it on the canvas
create_playlist_button_image = PhotoImage(
    file=relative_to_assets("button_2.png"))
create_playlist_button = Button(
    image=create_playlist_button_image,
    borderwidth=0,
    highlightthickness=0,
    command=create_new_playlist,
    relief="flat"
)
create_playlist_button.place(
    x=0.0,
    y=250.99999999999994,
    width=218.0,
    height=43.0
)

# Creates the radio tab button and places it on the canvas
radio_button_image = PhotoImage(
    file=relative_to_assets("button_3.png"))
radio_button = Button(
    image=radio_button_image,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_3 clicked"),
    relief="flat"
)
radio_button.place(
    x=0.0,
    y=181.99999999999994,
    width=218.0,
    height=43.0
)

# Creates the "Your Library" button and places it on the canvas
library_button_image = PhotoImage(
    file=relative_to_assets("button_4.png"))
library_button = Button(
    image=library_button_image,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_4 clicked"),
    relief="flat"
)
library_button.place(
    x=0.0,
    y=138.99999999999994,
    width=218.0,
    height=43.0
)

# Creates the search button and places it on the canvas
search_button_image = PhotoImage(
    file=relative_to_assets("button_5.png"))
search_button = Button(
    image=search_button_image,
    borderwidth=0,
    highlightthickness=0,
    command=search_tab,
    relief="flat"
)
search_button.place(
    x=0.0,
    y=95.99999999999994,
    width=218.0,
    height=43.0
)

# Creates the home button and places it on the canvas
home_button_image = PhotoImage(
    file=relative_to_assets("button_6.png"))
home_button = Button(
    image=home_button_image,
    borderwidth=0,
    highlightthickness=0,
    command=populate_playlists,
    relief="flat"
)
home_button.place(
    x=0.0,
    y=52.99999999999994,
    width=218.0,
    height=43.0
)

# Creates the Music placeholder logo image and places it on the canvas
image_image_23 = PhotoImage(
    file=relative_to_assets("image_23.png"))
image_23 = canvas.create_image(
    50.0,
    27.999999999999943,
    image=image_image_23
)

# Creates the three dots (extra settings) image and places it on the canvas
add_track_window_button_image = PhotoImage(
    file=relative_to_assets("image_24.png"))
add_track_window_button = canvas.create_image(
    188.0,
    27.999999999999943,
    image=add_track_window_button_image
)
canvas.tag_bind(add_track_window_button, "<ButtonPress-1>", lambda event: create_add_track_window())

# Creates the close window button and places it on the canvas
close_window_image = PhotoImage(
    file=relative_to_assets("button_7.png"))
close_window_button = Button(
    image=close_window_image,
    borderwidth=0,
    highlightthickness=0,
    command=close_main_window,
    relief="flat"
)
close_window_button.place(
    x=972.0,
    y=5.684341886080802e-14,
    width=52.0,
    height=33.0
)

# Creates the toggle fullscreen button and places it on the canvas
fullscreen_button_window_image = PhotoImage(
    file=relative_to_assets("button_8.png"))

windowed_button_image = PhotoImage(
    file=relative_to_assets("button_9.png"))

toggle_fullscreen_button = Button(
    image=windowed_button_image,
    borderwidth=0,
    highlightthickness=0,
    command=toggle_fullscreen,
    relief="flat"
)

toggle_fullscreen_button.place(
    x=920.0,
    y=5.684341886080802e-14,
    width=52.0,
    height=33.0
)

# Creates the minimize window button and places it on the canvas
minimize_window_image = PhotoImage(
    file=relative_to_assets("button_10.png"))
minimize_window_button = Button(
    image=minimize_window_image,
    borderwidth=0,
    highlightthickness=0,
    command=minimize_window,
    relief="flat",
)
minimize_window_button.place(
    x=868.0,
    y=5.684341886080802e-14,
    width=52.0,
    height=33.0,
)

# Pass GUI elements as parameters to the player module for easier acess
player.init(
    canvas, elapsed_time_text, track_slider, heart_button, heart_empty_image,
    heart_full_image, loop_button, no_loop_button_image, loop_button_image,
    play_button, play_button_image, pause_button_image, track_title_text, track_artist_text, total_time_text,
    album_cover_art, album_cover_art_image
)

# Call the mainloop of Tk
window.mainloop()