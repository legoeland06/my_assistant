def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    You must give a tuplet (r,g,b) like _from_rgb((125,125,125))"""
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"