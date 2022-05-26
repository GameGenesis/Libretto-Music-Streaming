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

from tkinter import END, WORD, Frame, Label, Scrollbar, Tk, Canvas, Entry, Text, Button, PhotoImage, Toplevel

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from database import Playlist, playlist_manager
import player
import utils


HIGH_RES = False

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")

GWL_STYLE = -16
GWLP_HWNDPARENT = -8
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000

INT = ctypes.c_int
LONG_PTR = ctypes.c_long

def _errcheck_not_zero(value, func, args):
    if value == 0:
        raise ctypes.WinError()
    return args

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

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def get_handle(root) -> int:
    root.update_idletasks()
    return GetWindowLongPtrW(root.winfo_id(), GWLP_HWNDPARENT)

def close_main_window():
    playlist_manager.close_session()
    window.destroy()

fullscreen = False

def toggle_fullscreen(event=None):
    global fullscreen
    if fullscreen == False:
        window.wm_state('zoomed')
        fullscreen = True
    else:
        window.wm_state('normal')
        fullscreen = False

def minimize_window():
    window.iconify()

def toggle_mute():
    global volume_indicator, high_volume_image, mute_volume_image
    if not player.stream or not player.stream.player:
        return

    if player.stream.player.audio_get_mute():
        player.stream.player.audio_set_mute(False)
        canvas.itemconfig(volume_indicator, image=high_volume_image)
    else:
        player.stream.player.audio_set_mute(True)
        canvas.itemconfig(volume_indicator, image=mute_volume_image)


window = Tk("Music Player")

if HIGH_RES:
    # DPI Awareness (Increase Pixels per inch)
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    window.geometry("1006x673")
else:
    window.geometry("+0+0")
    window.geometry("1008x680")

window.configure(bg = "#202020")

hwnd = get_handle(window)
style = GetWindowLongPtrW(hwnd, GWL_STYLE)
style &= ~(WS_CAPTION | WS_THICKFRAME)
SetWindowLongPtrW(hwnd, GWL_STYLE, style)

# App content

def populate_search_results():
    pass

def search_tab():
    global scroll_view_canvas, canvas
    global heart_empty_image

    scroll_view_canvas.yview_moveto(0)
    scroll_view_canvas.delete("track_element")
    scroll_view_canvas.delete("playlist_element")
    scroll_view_canvas.delete("search_tab_element")
    scroll_view_canvas.delete("search_result_element")

    scroll_view_canvas.images = list()

    search_bar_image = PhotoImage(
    file=relative_to_assets("image_46.png"))
    search_bar = scroll_view_canvas.create_image(
        621.0+82,
        82,
        image=search_bar_image,
        tag="search_tab_element"
    )

    cancel_search_button_image = PhotoImage(
        file=relative_to_assets("image_47.png"))
    cancel_search_button = scroll_view_canvas.create_image(
        973.0+82,
        81,
        image=cancel_search_button_image,
        tag="search_tab_element"
    )

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
    search_entry.insert(END, "Post Malone")
    search_entry_window = scroll_view_canvas.create_window(600, 82, window=search_entry)

    scroll_view_canvas.create_text(
        247.0+82,
        131.99999999999994,
        anchor="nw",
        text="Songs",
        fill="#FFFFFF",
        font=("RobotoRoman Medium", 16, "bold"),
        tag="search_result_element"
    )

    small_frame_image = PhotoImage(
        file=relative_to_assets("image_48.png"))
    small_frame = scroll_view_canvas.create_image(
        621.0+82,
        195.99999999999994,
        image=small_frame_image,
        tag="search_result_element"
    )

    cover_art_image = PhotoImage(
        file=relative_to_assets("image_49.png"))
    cover_art = scroll_view_canvas.create_image(
        276.0+82,
        195.99999999999994,
        image=cover_art_image,
        tag="search_result_element"
    )

    scroll_view_canvas.create_text(
        316.0+82,
        184.99999999999994,
        anchor="nw",
        text="Congratulations",
        fill="#FFFFFF",
        font=("RobotoRoman Medium", 12),
        tag="search_result_element"
    )

    scroll_view_canvas.create_text(
        560.0+82,
        184.99999999999994,
        anchor="nw",
        text="Post Malone",
        fill="#FFFFFF",
        font=("RobotoRoman Medium", 12),
        tag="search_result_element"
    )

    scroll_view_canvas.create_text(
        750.0+82,
        184.99999999999994,
        anchor="nw",
        text="Scorpion",
        fill="#FFFFFF",
        font=("RobotoRoman Medium", 12),
        tag="search_result_element"
    )

    scroll_view_canvas.create_text(
        931.0+82,
        184.99999999999994,
        anchor="nw",
        text="3:47",
        fill="#FFFFFF",
        font=("RobotoRoman Light", 9),
        tag="search_result_element"
    )

    heart_button = scroll_view_canvas.create_image(
        895.0+82,
        195.99999999999994,
        image=heart_empty_image,
        tag="search_result_element"
    )

    scroll_view_canvas.create_text(
        247.0+82,
        339.99999999999994,
        anchor="nw",
        text="YouTube",
        fill="#FFFFFF",
        font=("RobotoRoman Medium", 16, "bold"),
        tag="search_result_element"
    )

    large_frame_image = PhotoImage(
        file=relative_to_assets("image_50.png"))
    large_frame = scroll_view_canvas.create_image(
        621.0+82,
        421.99999999999994,
        image=large_frame_image,
        tag="search_result_element"
    )

    video_thumbnail_image = PhotoImage(
        file=relative_to_assets("image_51.png"))
    video_thumbnail = scroll_view_canvas.create_image(
        319.0+82,
        420.99999999999994,
        image=video_thumbnail_image,
        tag="search_result_element"
    )

    scroll_view_canvas.create_text(
        402.0+82,
        419.99999999999994,
        anchor="nw",
        text="Lea Makhoul",
        fill="#FFFFFF",
        font=("RobotoRoman Light", 10),
        tag="search_result_element"
    )

    scroll_view_canvas.create_text(
        402.0+82,
        400.99999999999994,
        anchor="nw",
        text="Lea Makhoul - RATATA (Official Music Video) ft. B.O.X",
        fill="#FFFFFF",
        font=("RobotoRoman Medium", 12),
        tag="search_result_element"
    )

    scroll_view_canvas.create_text(
        931.0+82,
        410.99999999999994,
        anchor="nw",
        text="3:08",
        fill="#FFFFFF",
        font=("RobotoRoman Light", 10),
        tag="search_result_element"
    )

    heart_button_2 = scroll_view_canvas.create_image(
        895.0+82,
        421.99999999999994,
        image=heart_empty_image,
        tag="search_result_element"
    )

    scroll_view_canvas.bind("<ButtonPress-1>", lambda event: scroll_view_canvas.focus_set())

    search_entry.bind("<FocusOut>", lambda event, c=scroll_view_canvas, w=search_entry_window, e=search_entry: check_textbox_content(c, w, e))
    
    scroll_view_canvas.tag_bind(search_bar, "<ButtonPress-1>", lambda event, c=scroll_view_canvas, w=search_entry_window, e=search_entry: edit_textbox(c, w, e))
    scroll_view_canvas.tag_bind(cancel_search_button, "<ButtonPress-1>", lambda event: search_entry.delete(0, END))

    scroll_view_canvas.images.append(search_bar_image)
    scroll_view_canvas.images.append(cancel_search_button_image)
    scroll_view_canvas.images.append(small_frame_image)
    scroll_view_canvas.images.append(cover_art_image)
    scroll_view_canvas.images.append(large_frame_image)
    scroll_view_canvas.images.append(video_thumbnail_image)

def check_textbox_content(canvas, canvas_window, text_entry):
    description_state = "normal"
    if type(text_entry) == Text:
        description_state = "hidden" if not text_entry.get("1.0", END).strip() else "normal"
    elif type(text_entry) == Entry:
        description_state = "hidden" if not text_entry.get() else "normal"

    canvas.itemconfigure(canvas_window, state=description_state)

def edit_textbox(canvas, canvas_window, text_entry):
    canvas.itemconfigure(canvas_window, state="normal")
    text_entry.focus()

def delete_playlist(overlay_window, playlist):
    playlist_manager.delete_playlist(playlist)
    close_toplevel_window(overlay_window)
    populate_playlists()

def save_playlist_details(overlay_window, playlist, title_entry, description_entry):
    current_title = playlist.title
    current_description = playlist.description
    new_title = title_entry.get()
    new_description = description_entry.get("1.0", END).strip()

    close_toplevel_window(overlay_window)

    if current_title == new_title and current_description == new_description:
        return

    if new_title and current_title != new_title and not playlist_manager.playlist_exists(new_title):
        playlist_manager.rename_playlist(playlist, new_title)
    if current_description != new_description:
        playlist_manager.edit_playlist_description(playlist, new_description)
    populate_tracks(playlist)

def close_toplevel_window(window):
    window.destroy()
    window.update()

def create_overlay_window() -> tuple[Toplevel, Canvas]:
    global window
    overlay_window = Toplevel(window)
    overlay_window.overrideredirect(True)
    overlay_window.geometry(f"1024x720+{window.winfo_x()}+{window.winfo_y()}")
    overlay_window.wm_attributes("-alpha", 0.65)
    overlay_window.configure(background="#101010")

    overlay_canvas = Canvas(overlay_window, width=1024, height=720, highlightthickness=0)
    overlay_rectangle = overlay_canvas.create_rectangle(0, 0, 1024, 720, fill="#101010")
    overlay_canvas.tag_bind(overlay_rectangle, "<ButtonPress-1>", lambda event: close_toplevel_window(overlay_window))
    overlay_canvas.pack()

    window.bind("<Unmap>", lambda event: close_toplevel_window(overlay_window))

    return overlay_window, overlay_canvas

def create_edit_window() -> tuple[Toplevel, Toplevel, Canvas]:
    overlay_window, overlay_canvas = create_overlay_window()
    edit_window = Toplevel(overlay_window)
    edit_window.overrideredirect(True)
    edit_window.geometry(f"1024x720+{window.winfo_x()}+{window.winfo_y()}")

    edit_window.config(background="red")
    edit_window.attributes("-transparentcolor", "red")

    edit_window.wm_attributes("-topmost", True)
    edit_window.update()
    edit_window.wm_attributes("-topmost", False)

    edit_canvas = Canvas(edit_window, width=1024, height=720, highlightthickness=0, bg="red")
    edit_canvas.pack()

    return overlay_window, edit_window, edit_canvas

def create_rename_window(playlist):
    overlay_window, edit_window, edit_canvas = create_edit_window()
    edit_canvas.images = list()

    playlist_details_box_image = PhotoImage(
    file=relative_to_assets("image_35.png"))
    playlist_details_box = edit_canvas.create_image(
        512.0,
        335.99999999999994,
        image=playlist_details_box_image
    )

    title_entry_image = PhotoImage(
        file=relative_to_assets("image_36.png"))
    title_textbox = edit_canvas.create_image(
        598.0,
        270.99999999999994,
        image=title_entry_image
    )

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
    title_entry.insert(END, playlist.title)
    title_entry_window = edit_canvas.create_window(597, 271, window=title_entry)

    description_entry_image = PhotoImage(
        file=relative_to_assets("image_37.png"))
    description_textbox = edit_canvas.create_image(
        598.0,
        356.99999999999994,
        image=description_entry_image
    )

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
    description_entry.insert("1.0", playlist.description)

    description_entry_window = edit_canvas.create_window(597, 356, window=description_entry)
    check_textbox_content(edit_canvas, description_entry_window, description_entry)

    playlist_image = PhotoImage(
        file=relative_to_assets("image_41.png" if playlist.title == "Liked Songs" else "image_40.png"))
    edit_canvas.create_image(
        378.0,
        331.99999999999994,
        image=playlist_image
    )

    save_button_image = PhotoImage(
        file=relative_to_assets("image_38.png"))
    save_button = edit_canvas.create_image(
        674.0,
        448.99999999999994,
        image=save_button_image
    )

    delete_button_image = PhotoImage(
    file=relative_to_assets("image_45.png"))
    delete_button = edit_canvas.create_image(
        557.0,
        448.99999999999994,
        image=delete_button_image
    )

    close_button_image = PhotoImage(
        file=relative_to_assets("image_39.png"))
    close_button = edit_canvas.create_image(
        720.0,
        215.99999999999994,
        image=close_button_image
    )


    edit_canvas.tag_bind(description_textbox, "<ButtonPress-1>", lambda event, c=edit_canvas, w=description_entry_window, e=description_entry: edit_textbox(c, w, e))
    edit_canvas.tag_bind(title_textbox, "<ButtonPress-1>", lambda event, c=edit_canvas, w=title_entry_window, e=title_entry: edit_textbox(c, w, e))
    edit_canvas.tag_bind(playlist_details_box, "<ButtonPress-1>", lambda event: edit_canvas.focus_set())

    description_entry.bind("<FocusOut>", lambda event, c=edit_canvas, w=description_entry_window, e=description_entry: check_textbox_content(c, w, e))
    title_entry.bind("<FocusOut>", lambda event, c=edit_canvas, w=title_entry_window, e=title_entry: check_textbox_content(c, w, e))

    title_entry.bind("<Return>", lambda event, w=overlay_window, p=playlist, t=title_entry, d=description_entry: save_playlist_details(w, p, t, d))
    description_entry.bind("<Return>", lambda event, w=overlay_window, p=playlist, t=title_entry, d=description_entry: save_playlist_details(w, p, t, d))

    edit_canvas.tag_bind(delete_button, "<ButtonPress-1>", lambda event, w=overlay_window, p=playlist: delete_playlist(w, p))
    edit_canvas.tag_bind(save_button, "<ButtonPress-1>", lambda event, w=overlay_window, p=playlist, t=title_entry, d=description_entry: save_playlist_details(w, p, t, d))
    edit_canvas.tag_bind(close_button, "<ButtonPress-1>", lambda event: overlay_window.destroy())

    edit_canvas.images.append(playlist_details_box_image)
    edit_canvas.images.append(title_entry_image)
    edit_canvas.images.append(description_entry_image)
    edit_canvas.images.append(playlist_image)
    edit_canvas.images.append(save_button_image)
    edit_canvas.images.append(delete_button_image)
    edit_canvas.images.append(close_button_image)

def toggle_edit_details_popup(playlist_title: int, hidden: bool=False):
    global scroll_view_canvas
    state = "hidden" if hidden else "normal"
    scroll_view_canvas.itemconfigure(playlist_title, state=state)

def populate_tracks(playlist: Playlist):
    global scroll_view_canvas, canvas, track_title_text, track_artist_text
    global heart_button, heart_empty_image, heart_full_image
    global play_button, pause_button_image, play_button_image
    global total_time_text

    scroll_view_canvas.yview_moveto(0)
    scroll_view_canvas.delete("track_element")
    scroll_view_canvas.delete("playlist_element")
    scroll_view_canvas.delete("search_tab_element")
    scroll_view_canvas.delete("search_result_element")

    scroll_view_canvas.create_rectangle(
        300.0,
        33.0,
        1106.0,
        241.0,
        fill="#292929",
        outline="",
        tag="track_element"
    )

    playlist_image = PhotoImage(
        file=relative_to_assets("image_41.png" if playlist.title == "Liked Songs" else "image_40.png"))
    scroll_view_canvas.create_image(
        326.0+82,
        135.99999999999994,
        image=playlist_image,
        tag="track_element"
    )

    playlist_title_name = player.truncate_string(playlist.title, 20)
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

    edit_details_image = PhotoImage(
    file=relative_to_assets("image_42.png"))
    edit_details_popup = scroll_view_canvas.create_image(
        title_text_bounds[2] + 25.0,
        113.0,
        image=edit_details_image,
        state = "hidden"
    )

    if playlist.title != "Liked Songs":
        scroll_view_canvas.tag_bind(playlist_title, "<Enter>", lambda event: toggle_edit_details_popup(edit_details_popup, False))
        scroll_view_canvas.tag_bind(playlist_title, "<Leave>", lambda event: toggle_edit_details_popup(edit_details_popup, True))
        scroll_view_canvas.tag_bind(playlist_title, "<ButtonPress-1>", lambda event, playlist=playlist: create_rename_window(playlist))

    scroll_view_canvas.create_text(
        433.0+82,
        135.0,
        anchor="nw",
        text="Ryan",
        fill="#FFFFFF",
        font=("RobotoRoman Light", 14),
        tag="track_element"
    )

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

    shuffle_image = PhotoImage(
        file=relative_to_assets("image_34.png"))
    scroll_view_canvas.create_image(
        935.0+82,
        170.0,
        image=shuffle_image,
        tag="track_element"
    )

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

    scroll_view_canvas.create_text(
        270.0+82,
        265.99999999999994,
        anchor="nw",
        text="#",
        fill="#FFFFFF",
        font=("RobotoRoman Light", 12),
        tag="track_element"
    )

    scroll_view_canvas.create_text(
        331.0+82,
        265.99999999999994,
        anchor="nw",
        text="Title",
        fill="#FFFFFF",
        font=("RobotoRoman Light", 12),
        tag="track_element"
    )

    scroll_view_canvas.create_text(
        496.0+82,
        265.99999999999994,
        anchor="nw",
        text="Artist",
        fill="#FFFFFF",
        font=("RobotoRoman Light", 12),
        tag="track_element"
    )

    scroll_view_canvas.create_text(
        645.0+82,
        265.99999999999994,
        anchor="nw",
        text="Album",
        fill="#FFFFFF",
        font=("RobotoRoman Light", 12),
        tag="track_element"
    )

    scroll_view_canvas.create_text(
        791.0+82,
        265.99999999999994,
        anchor="nw",
        text="Date Added",
        fill="#FFFFFF",
        font=("RobotoRoman Light", 12),
        tag="track_element"
    )

    duration_image = PhotoImage(
        file=relative_to_assets("image_29.png"))
    scroll_view_canvas.create_image(
        948.0+82,
        273.99999999999994,
        image=duration_image,
        tag="track_element"
    )

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
        final_row = row + 1
        objs = list()

        track_frame_image = PhotoImage(
            file=relative_to_assets("image_30.png"))
        objs.append(scroll_view_canvas.create_image(
            621.0+82,
            324.99999999999994 + (row * 52),
            image=track_frame_image,
            tag="track_element"
        ))

        objs.append(scroll_view_canvas.create_text(
            270.0+82,
            314.99999999999994 + (row * 52),
            anchor="nw",
            text=str(row+1),
            fill="#FFFFFF",
            font=("RobotoRoman Medium", 12),
            tag="track_element"
        ))

        track_title = player.truncate_string(track.title, 18)
        objs.append(scroll_view_canvas.create_text(
            331.0+82,
            314.99999999999994 + (row * 52),
            anchor="nw",
            text=track_title,
            fill="#FFFFFF",
            font=("RobotoRoman Medium", 12),
            tag="track_element"
        ))

        track_artist = player.truncate_string(track.artist, 16)
        objs.append(scroll_view_canvas.create_text(
            496.0+82,
            314.99999999999994 + (row * 52),
            anchor="nw",
            text=track_artist,
            fill="#FFFFFF",
            font=("RobotoRoman Medium", 12),
            tag="track_element"
        ))

        track_album = player.truncate_string(track.album, 16)
        objs.append(scroll_view_canvas.create_text(
            645.0+82,
            314.99999999999994 + (row * 52),
            anchor="nw",
            text=track_album,
            fill="#FFFFFF",
            font=("RobotoRoman Medium", 12),
            tag="track_element"
        ))

        objs.append(scroll_view_canvas.create_text(
            791.0+82,
            315.99999999999994 + (row * 52),
            anchor="nw",
            text="2018-12-04",
            fill="#CCCCCC",
            font=("RobotoRoman Light", 11),
            tag="track_element"
        ))

        track_duration = player.get_formatted_time(track.duration)
        objs.append(scroll_view_canvas.create_text(
            947.0+82,
            314.99999999999994 + (row * 52),
            anchor="n",
            text=track_duration,
            fill="#CCCCCC",
            font=("RobotoRoman Light", 11),
            tag="track_element"
        ))
        scroll_view_canvas.images.append(track_frame_image)
        for obj in objs:
            scroll_view_canvas.tag_bind(obj, "<ButtonPress-1>",
                lambda event, track_id=track.id:
                player.play_new_track(canvas, track_id, track_title_text, track_artist_text,
                    heart_button, heart_empty_image, heart_full_image, play_button, play_button_image, pause_button_image, total_time_text))

    scroll_view_canvas.create_rectangle(
        300.0,
        330.0 + (final_row * 52.0),
        1106.0,
        340.0 + (final_row * 52.0),
        fill="#202020",
        outline="",
        tag="track_element"
    )

    scroll_view_canvas.images.append(playlist_image)
    scroll_view_canvas.images.append(edit_details_image)
    scroll_view_canvas.images.append(play_image)
    scroll_view_canvas.images.append(pause_image)
    scroll_view_canvas.images.append(shuffle_image)
    scroll_view_canvas.images.append(download_image)
    scroll_view_canvas.images.append(downloaded_image)
    scroll_view_canvas.images.append(duration_image)
    onFrameConfigure(scroll_view_canvas)

def populate_playlists():
    global scroll_view_canvas, canvas

    scroll_view_canvas.yview_moveto(0)
    scroll_view_canvas.delete("track_element")
    scroll_view_canvas.delete("playlist_element")
    scroll_view_canvas.delete("search_tab_element")
    scroll_view_canvas.delete("search_result_element")

    scroll_view_canvas.images = list()

    playlist_rows = player.split_list(playlist_manager.session.query(Playlist).all(), 3)

    for row, playlists in enumerate(playlist_rows):
        for column, playlist in enumerate(playlists):
            objs = list()
            frame_image = PhotoImage(
                file=relative_to_assets("image_25.png"))
            objs.append(scroll_view_canvas.create_image(
                418.0 + (column * 208),
                177.99999999999994 + (row * 260),
                image=frame_image,
                tag="playlist_element"
            ))

            playlist_title = player.truncate_string(playlist.title, 20)
            objs.append(scroll_view_canvas.create_text(
                352.0 + (column * 208),
                230.99999999999994 + (row * 260),
                anchor="nw",
                text=playlist_title,
                fill="#FFFFFF",
                font=("RobotoRoman Medium", 11, "bold"),
                tag="playlist_element"
            ))

            objs.append(scroll_view_canvas.create_text(
                352.0 + (column * 208),
                254.99999999999994 + (row * 260),
                anchor="nw",
                text="Ryan",
                fill="#DDDDDD",
                font=("RobotoRoman Light", 10),
                tag="playlist_element"
            ))

            playlist_image = PhotoImage(
                file=relative_to_assets("image_27.png" if playlist.title == "Liked Songs" else "image_26.png"))
            objs.append(scroll_view_canvas.create_image(
                418.0 + (column * 208),
                149.99999999999994 + (row * 260),
                image=playlist_image,
                tag="playlist_element"
            ))
            scroll_view_canvas.images.append(frame_image)
            scroll_view_canvas.images.append(playlist_image)
            for obj in objs:
                scroll_view_canvas.tag_bind(obj, "<ButtonPress-1>",
                    lambda event, playlist=playlist:
                        populate_tracks(playlist))

    onFrameConfigure(scroll_view_canvas)

def create_new_playlist():
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

def view_liked_songs():
    liked_songs_playlist = playlist_manager.get_or_create_playlist("Liked Songs")
    populate_tracks(liked_songs_playlist)

def onFrameConfigure(canvas):
    """Reset the scroll region to encompass the inner frame"""
    canvas.configure(scrollregion=canvas.bbox("all"))

def bound_to_mousewheel(event):
    global scroll_view_canvas
    scroll_view_canvas.bind_all("<MouseWheel>", on_mousewheel)

def unbound_to_mousewheel(event):
    global scroll_view_canvas
    scroll_view_canvas.unbind_all("<MouseWheel>")

def on_mousewheel(event):
    # This code was modified using this source: https://stackoverflow.com/a/37861801
    global scroll_view_canvas
    scroll_view_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

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
canvas.create_rectangle(
    218.0,
    0.0,
    1024.0,
    640.0,
    fill="#202020",
    outline=""
)

scroll_view_canvas = Canvas(
    window,
    borderwidth=0,
    background="#202020",
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)
scroll_view_canvas.place(x=218.0, y=33.0, width=806.0, height=607.0)

frame = Frame(scroll_view_canvas, background="#202020", width=806.0, padx=20.0, pady=20.0)

scroll_view_canvas.create_window(
    (300,33),
    window=frame,
    anchor="nw"
)

scroll_view_canvas.bind('<Enter>', bound_to_mousewheel)
scroll_view_canvas.bind('<Leave>', unbound_to_mousewheel)

frame.bind("<Configure>", lambda event, canvas=scroll_view_canvas: onFrameConfigure(scroll_view_canvas))

canvas.create_rectangle(
    0.0,
    640.0,
    1024.0,
    720.0,
    fill="#303030",
    outline=""
)

def start_move(event):
    global x, y
    window.geometry("1024x720")
    window.wm_overrideredirect(True)
    x = event.x
    y = event.y

def stop_move(event):
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
    global x, y

    if x and y:
        window.geometry(f'+{event.x_root - x}+{event.y_root - y}')

title_bar_frame = canvas.create_rectangle(
    0.0,
    0.0,
    1024.0,
    33.0,
    fill="#313131",
    outline=""
)

canvas.tag_bind(title_bar_frame, "<ButtonPress-1>", start_move)
canvas.tag_bind(title_bar_frame, "<ButtonRelease-1>", stop_move)
canvas.tag_bind(title_bar_frame, "<B1-Motion>", do_move)
canvas.tag_bind(title_bar_frame, '<Double-1>', toggle_fullscreen)

playlist_manager.open_session()
populate_playlists()


"""
---------------------------------------------------------------------------------------------------------
Most of the basic GUI code below was generated using Tkinter Designer: https://github.com/ParthJadhav/Tkinter-Designer,
and was later modified to fit the specific needs of the application
---------------------------------------------------------------------------------------------------------
"""


play_button_image = PhotoImage(
    file=relative_to_assets("image_1.png"))
pause_button_image = PhotoImage(
    file=relative_to_assets("image_2.png"))
play_button = canvas.create_image(
    511.0,
    669.0,
    image=play_button_image
)

canvas.tag_bind(play_button, "<ButtonPress-1>", lambda event:
    player.play_pause_track(canvas, play_button, play_button_image, pause_button_image))

image_image_3 = PhotoImage(
    file=relative_to_assets("image_3.png"))
image_3 = canvas.create_image(
    561.0,
    671.0,
    image=image_image_3
)

image_image_4 = PhotoImage(
    file=relative_to_assets("image_4.png"))
image_4 = canvas.create_image(
    460.0,
    671.0,
    image=image_image_4
)

skip_backwards_button_image = PhotoImage(
    file=relative_to_assets("image_5.png"))
skip_backwards_button = canvas.create_image(
    416.0,
    670.0,
    image=skip_backwards_button_image
)

canvas.tag_bind(skip_backwards_button, "<ButtonPress-1>", lambda event: player.skip_backwards())

skip_forwards_button_image = PhotoImage(
    file=relative_to_assets("image_6.png"))
skip_forwards_button = canvas.create_image(
    602.0,
    670.0,
    image=skip_forwards_button_image
)

canvas.tag_bind(skip_forwards_button, "<ButtonPress-1>", lambda event: player.skip_forwards())

image_image_7 = PhotoImage(
    file=relative_to_assets("image_7.png"))
image_7 = canvas.create_image(
    375.0,
    671.0,
    image=image_image_7
)

no_loop_button_image = PhotoImage(
    file=relative_to_assets("image_8.png"))
loop_button_image = PhotoImage(
    file=relative_to_assets("image_9.png"))
loop_button = canvas.create_image(
    644.0,
    671.0,
    image=no_loop_button_image
)

canvas.tag_bind(loop_button, "<ButtonPress-1>", lambda event: player.toggle_loop(canvas, loop_button, no_loop_button_image, loop_button_image))

track_slider = utils.Slider(canvas, 317.0, 699.0, 707.0, 704.0)

elapsed_time_text = canvas.create_text(
    310.0,
    694.0,
    anchor="ne",
    text="0:00",
    fill="#FFFFFF",
    font=("RobotoRoman Light", 9)
)

total_time_text = canvas.create_text(
    715.0,
    694.0,
    anchor="nw",
    text="0:00",
    fill="#FFFFFF",
    font=("RobotoRoman Light", 9)
)

image_image_12 = PhotoImage(
    file=relative_to_assets("image_12.png"))
image_12 = canvas.create_image(
    43.0,
    681.0,
    image=image_image_12
)

track_artist_text = canvas.create_text(
    85.0,
    683.0,
    anchor="nw",
    text="Post Malone",
    fill="#DDDDDD",
    font=("RobotoRoman Light", 10)
)

track_title_text = canvas.create_text(
    85.0,
    663.0,
    anchor="nw",
    text="Congratulations",
    fill="#FFFFFF",
    font=("RobotoRoman Medium", 12, "bold")
)

heart_empty_image = PhotoImage(
    file=relative_to_assets("image_13.png"))

heart_full_image = PhotoImage(
    file=relative_to_assets("image_14.png"))

heart_button = canvas.create_image(
    235.0,
    684.0,
    image=heart_empty_image
)

image_image_15 = PhotoImage(
    file=relative_to_assets("image_15.png"))
image_15 = canvas.create_image(
    796.0,
    678.0,
    image=image_image_15
)

image_image_16 = PhotoImage(
    file=relative_to_assets("image_16.png"))
image_16 = canvas.create_image(
    829.0,
    678.0,
    image=image_image_16
)

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

image_image_21 = PhotoImage(
    file=relative_to_assets("image_21.png"))
image_21 = canvas.create_image(
    935.0,
    678.0,
    image=image_image_21
)

image_image_22 = PhotoImage(
    file=relative_to_assets("image_22.png"))
image_22 = canvas.create_image(
    910.0,
    678.0,
    image=image_image_22
)

canvas.create_rectangle(
    0.0,
    0.0,
    218.0,
    640.0,
    fill="#009CDF",
    outline="")

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=view_liked_songs,
    relief="flat"
)
button_1.place(
    x=0.0,
    y=293.99999999999994,
    width=218.0,
    height=43.0
)

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=create_new_playlist,
    relief="flat"
)
button_2.place(
    x=0.0,
    y=250.99999999999994,
    width=218.0,
    height=43.0
)

button_image_3 = PhotoImage(
    file=relative_to_assets("button_3.png"))
button_3 = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_3 clicked"),
    relief="flat"
)
button_3.place(
    x=0.0,
    y=181.99999999999994,
    width=218.0,
    height=43.0
)

button_image_4 = PhotoImage(
    file=relative_to_assets("button_4.png"))
button_4 = Button(
    image=button_image_4,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_4 clicked"),
    relief="flat"
)
button_4.place(
    x=0.0,
    y=138.99999999999994,
    width=218.0,
    height=43.0
)

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

button_image_6 = PhotoImage(
    file=relative_to_assets("button_6.png"))
button_6 = Button(
    image=button_image_6,
    borderwidth=0,
    highlightthickness=0,
    command=populate_playlists,
    relief="flat"
)
button_6.place(
    x=0.0,
    y=52.99999999999994,
    width=218.0,
    height=43.0
)

image_image_23 = PhotoImage(
    file=relative_to_assets("image_23.png"))
image_23 = canvas.create_image(
    50.0,
    27.999999999999943,
    image=image_image_23
)

image_image_24 = PhotoImage(
    file=relative_to_assets("image_24.png"))
image_24 = canvas.create_image(
    188.0,
    27.999999999999943,
    image=image_image_24
)

button_image_7 = PhotoImage(
    file=relative_to_assets("button_7.png"))
button_7 = Button(
    image=button_image_7,
    borderwidth=0,
    highlightthickness=0,
    command=close_main_window,
    relief="flat"
)
button_7.place(
    x=972.0,
    y=5.684341886080802e-14,
    width=52.0,
    height=33.0
)

button_image_8 = PhotoImage(
    file=relative_to_assets("button_8.png"))
button_8 = Button(
    image=button_image_8,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_8 clicked"),
    relief="flat"
)
button_8.place(
    x=920.0,
    y=5.684341886080802e-14,
    width=52.0,
    height=33.0
)

button_image_9 = PhotoImage(
    file=relative_to_assets("button_9.png"))
button_9 = Button(
    image=button_image_9,
    borderwidth=0,
    highlightthickness=0,
    command=toggle_fullscreen,
    relief="flat"
)
button_9.place(
    x=920.0,
    y=5.684341886080802e-14,
    width=52.0,
    height=33.0
)

button_image_10 = PhotoImage(
    file=relative_to_assets("button_10.png"))
button_10 = Button(
    image=button_image_10,
    borderwidth=0,
    highlightthickness=0,
    command=minimize_window,
    relief="flat",
)
button_10.place(
    x=868.0,
    y=5.684341886080802e-14,
    width=52.0,
    height=33.0,
)

player.init(canvas, elapsed_time_text, track_slider)
window.mainloop()