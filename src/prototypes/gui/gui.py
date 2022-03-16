# Basic UI imported from Figma using Tkinter Designer
# https://github.com/ParthJadhav/Tkinter-Designer

from ctypes.wintypes import BOOL, HWND, LONG
import ctypes
from pathlib import Path

from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage

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

def toggle_fullscreen():
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
    window.geometry("1008x680")

window.configure(bg = "#FFFFFF")

hwnd = get_handle(window)
style = GetWindowLongPtrW(hwnd, GWL_STYLE)
style &= ~(WS_CAPTION | WS_THICKFRAME)
SetWindowLongPtrW(hwnd, GWL_STYLE, style)

canvas = Canvas(
    window,
    bg = "#FFFFFF",
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
    outline="")

canvas.create_rectangle(
    0.0,
    640.0,
    1024.0,
    720.0,
    fill="#303030",
    outline="")

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