"""
Most of the basic GUI code was generated using Tkinter Designer: https://github.com/ParthJadhav/Tkinter-Designer,
and was later modified to fit the specific needs of the application

Most of the icons used are Google's Material Icons: https://developers.google.com/fonts/docs/material_icons, inserted into
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
import threading

from tkinter import Frame, Label, Scrollbar, Tk, Canvas, Entry, Text, Button, PhotoImage

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from database import Playlist, PlaylistManager
from stream import Stream

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

# ------------------- Test Code -------------------

music_thread = None
stream = None

def play_track(url):
    global music_thread, stream
    if stream:
        stream.stop()
    if music_thread:
        music_thread.join()

    stream = Stream(url)
    music_thread = threading.Thread(target=lambda: stream.play(False))
    #make test_loop terminate when the user exits the window
    music_thread.daemon = True 
    music_thread.start()

def populate_tracks(tracks):
    global widgets
    for widget in widgets:
        widget.destroy()

    for row, track in enumerate(tracks):
        button = Button(frame, text=track.title, borderwidth=0, relief="flat", command=lambda t=track.stream.url: play_track(t))
        button.grid(row=row, column=2)
        widgets.append(button)

def populate(frame):
    global widgets
    pm = PlaylistManager()
    playlists = pm.session.query(Playlist).all()
    for row, playlist in enumerate(playlists):
        Label(frame, text=row, width=3, borderwidth=0, relief="flat").grid(row=row, column=0)
        Button(frame, text=playlist.title, borderwidth=0, highlightthickness=0,
            command=lambda t=playlist.tracks: populate_tracks(t), relief="flat").grid(row=row, column=1)

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

scroll_view_canvas = Canvas(window, borderwidth=0, background="#202020", bd = 0, highlightthickness = 0, relief = "ridge")

frame = Frame(scroll_view_canvas, background="#202020", width=806.0, padx=20.0, pady=20.0)
vsb = Scrollbar(window, orient="vertical", command=scroll_view_canvas.yview)
vsb.lift(frame)
vsb.place(x=1007.0, y=33.0, height=607.0)

scroll_view_canvas.bind('<Enter>', bound_to_mousewheel)
scroll_view_canvas.bind('<Leave>', unbound_to_mousewheel)

scroll_view_canvas.configure(yscrollcommand=vsb.set)

scroll_view_canvas.place(x=218.0, y=33.0, width=806.0, height=607.0)
scroll_view_canvas.create_window((300,33), window=frame, anchor="nw")

frame.bind("<Configure>", lambda event, canvas=scroll_view_canvas: onFrameConfigure(scroll_view_canvas))

widgets = []
# populate(frame)

image_image_25 = PhotoImage(
    file=relative_to_assets("image_25.png"))
image_25 = scroll_view_canvas.create_image(
    336.0+80,
    177.99999999999994,
    image=image_image_25
)

image_image_26 = PhotoImage(
    file=relative_to_assets("image_26.png"))
image_26 = scroll_view_canvas.create_image(
    336.0+80,
    147.99999999999994,
    image=image_image_26
)

scroll_view_canvas.create_text(
    270.0+80,
    230.99999999999994,
    anchor="nw",
    text="Post Malone",
    fill="#FFFFFF",
    font=("RobotoRoman Medium", 12, "bold")
)

scroll_view_canvas.create_text(
    270.0+80,
    254.99999999999994,
    anchor="nw",
    text="Author",
    fill="#DDDDDD",
    font=("RobotoRoman Light", 10)
)

image_image_27 = PhotoImage(
    file=relative_to_assets("image_27.png"))
image_27 = scroll_view_canvas.create_image(
    544.0+80,
    177.99999999999994,
    image=image_image_27
)

scroll_view_canvas.create_text(
    478.0+80,
    230.99999999999994,
    anchor="nw",
    text="Favorite Tracks",
    fill="#FFFFFF",
    font=("RobotoRoman Medium", 12, "bold")
)

scroll_view_canvas.create_text(
    478.0+80,
    254.99999999999994,
    anchor="nw",
    text="Ryan",
    fill="#DDDDDD",
    font=("RobotoRoman Light", 10)
)

image_image_28 = PhotoImage(
    file=relative_to_assets("image_28.png"))
image_28 = scroll_view_canvas.create_image(
    544.0+80,
    149.99999999999994,
    image=image_image_28
)

image_image_29 = PhotoImage(
    file=relative_to_assets("image_29.png"))
image_29 = scroll_view_canvas.create_image(
    752.0+80,
    177.99999999999994,
    image=image_image_29
)

scroll_view_canvas.create_text(
    686.0+80,
    230.99999999999994,
    anchor="nw",
    text="Favorite Tracks",
    fill="#FFFFFF",
    font=("RobotoRoman Medium", 12, "bold")
)

scroll_view_canvas.create_text(
    686.0+80,
    254.99999999999994,
    anchor="nw",
    text="Ryan",
    fill="#DDDDDD",
    font=("RobotoRoman Light", 10)
)

image_image_30 = PhotoImage(
    file=relative_to_assets("image_30.png"))
image_30 = scroll_view_canvas.create_image(
    752.0+80,
    149.99999999999994,
    image=image_image_30
)

# -------------------------------------------------

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
    fill="#202020",
    outline=""
)

canvas.tag_bind(title_bar_frame, "<ButtonPress-1>", start_move)
canvas.tag_bind(title_bar_frame, "<ButtonRelease-1>", stop_move)
canvas.tag_bind(title_bar_frame, "<B1-Motion>", do_move)
canvas.tag_bind(title_bar_frame, '<Double-1>', toggle_fullscreen)

image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    511.0,
    669.0,
    image=image_image_1
)

image_image_2 = PhotoImage(
    file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    511.0,
    669.0,
    image=image_image_2
)

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

image_image_5 = PhotoImage(
    file=relative_to_assets("image_5.png"))
image_5 = canvas.create_image(
    416.0,
    670.0,
    image=image_image_5
)

image_image_6 = PhotoImage(
    file=relative_to_assets("image_6.png"))
image_6 = canvas.create_image(
    602.0,
    670.0,
    image=image_image_6
)

image_image_7 = PhotoImage(
    file=relative_to_assets("image_7.png"))
image_7 = canvas.create_image(
    375.0,
    671.0,
    image=image_image_7
)

image_image_8 = PhotoImage(
    file=relative_to_assets("image_8.png"))
image_8 = canvas.create_image(
    644.0,
    671.0,
    image=image_image_8
)

image_image_9 = PhotoImage(
    file=relative_to_assets("image_9.png"))
image_9 = canvas.create_image(
    644.0,
    671.0,
    image=image_image_9
)

image_image_10 = PhotoImage(
    file=relative_to_assets("image_10.png"))
image_10 = canvas.create_image(
    512.0,
    702.0,
    image=image_image_10
)

image_image_11 = PhotoImage(
    file=relative_to_assets("image_11.png"))
image_11 = canvas.create_image(
    445.0,
    702.0,
    image=image_image_11
)

canvas.create_text(
    310.0,
    694.0,
    anchor="ne",
    text="1:48",
    fill="#FFFFFF",
    font=("RobotoRoman Light", 12 * -1)
)

canvas.create_text(
    715.0,
    694.0,
    anchor="nw",
    text="2:36",
    fill="#FFFFFF",
    font=("RobotoRoman Light", 12 * -1)
)

image_image_12 = PhotoImage(
    file=relative_to_assets("image_12.png"))
image_12 = canvas.create_image(
    43.0,
    681.0,
    image=image_image_12
)

canvas.create_text(
    90.0,
    680.0,
    anchor="nw",
    text="Post Malone",
    fill="#FFFFFF",
    font=("RobotoRoman Light", 14 * -1)
)

canvas.create_text(
    90.0,
    660.0,
    anchor="nw",
    text="Congratulations",
    fill="#FFFFFF",
    font=("RobotoRoman Medium", 16 * -1)
)

image_image_13 = PhotoImage(
    file=relative_to_assets("image_13.png"))
image_13 = canvas.create_image(
    235.0,
    684.0,
    image=image_image_13
)

image_image_14 = PhotoImage(
    file=relative_to_assets("image_14.png"))
image_14 = canvas.create_image(
    235.0,
    684.0,
    image=image_image_14
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

image_image_17 = PhotoImage(
    file=relative_to_assets("image_17.png"))
image_17 = canvas.create_image(
    856.0,
    677.0,
    image=image_image_17
)

image_image_18 = PhotoImage(
    file=relative_to_assets("image_18.png"))
image_18 = canvas.create_image(
    858.0,
    677.0,
    image=image_image_18
)

image_image_19 = PhotoImage(
    file=relative_to_assets("image_19.png"))
image_19 = canvas.create_image(
    861.0,
    677.0,
    image=image_image_19
)

image_image_20 = PhotoImage(
    file=relative_to_assets("image_20.png"))
image_20 = canvas.create_image(
    861.0,
    677.0,
    image=image_image_20
)

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
    command=lambda: print("button_1 clicked"),
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
    command=lambda: print("button_2 clicked"),
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

button_image_5 = PhotoImage(
    file=relative_to_assets("button_5.png"))
button_5 = Button(
    image=button_image_5,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_5 clicked"),
    relief="flat"
)
button_5.place(
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
    command=lambda: print("button_6 clicked"),
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
    command=lambda: window.destroy(),
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
window.mainloop()