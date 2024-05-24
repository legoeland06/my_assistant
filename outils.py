import tkinter
import tkinter.font as tkfont
from SimpleMarkdownText import SimpleMarkdownText


def from_rgb_to_tkColors(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    You must give a tuplet (r,g,b) like _from_rgb((125,125,125))"""
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


def bold_it(obj: tkinter.Text | SimpleMarkdownText):
    return tkfont.Font(**obj.configure())
