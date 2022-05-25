from tkinter import Canvas


def clamp(value: float, min_value: float, max_value: float):
    return max(min(value, max_value), min_value)

def clamp_01(value: float):
    return clamp(value, 0.0, 1.0)

def lerp(a: float, b: float, t: float):
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
    t = clamp_01(t)
    return a + (b - a) * t

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