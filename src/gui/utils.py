from tkinter import Canvas


def lerp(a, b, percent):
    return a + percent * (b - a)

def round_rectangle(canvas: Canvas, x1: float, y1: float, x2: float, y2: float, radius: int=25, **kwargs):
    # Source: https://stackoverflow.com/a/44100075
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
        bg="#838383", fg="#DADADA") -> None:
        self.canvas = canvas

        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.start_pos, self.end_pos = x1, x2

        self.radius, self.bg, self.fg = radius, bg, fg

        self.slider_background = round_rectangle(canvas, x1, y1, x2, y2, radius=radius, fill=bg)
        self.slider_foreground = round_rectangle(canvas, x1, y1, x1, y2, radius=0, fill=fg)

    def set_position(self, percent: float):
        self.current_pos = lerp(self.start_pos, self.end_pos, percent)
        self.canvas.delete(self.slider_foreground)
        self.slider_foreground = round_rectangle(self.canvas, self.x1, self.y1, self.current_pos, self.y2, radius=self.radius, fill=self.fg)