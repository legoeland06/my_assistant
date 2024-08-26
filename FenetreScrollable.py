import tkinter as tk
import tkinter.font as tkfont


from Constants import DARK2, ZEFONT
from outils import (
    from_rgb_to_tkColors,
)


class FenetreScrollable(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.prompts_history = []
        self.fontdict = tkfont.Font(
            family=ZEFONT[0],
            size=ZEFONT[1],
            slant=ZEFONT[2],
            weight=ZEFONT[3],
        )
        self.canvas = tk.Canvas(
            self,
            borderwidth=0,
            background=from_rgb_to_tkColors(DARK2),
        )
        self.frame = tk.Frame(
            self.canvas,
            background=from_rgb_to_tkColors(DARK2),
        )
        self.vScrollbar = tk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.vScrollbar.set)

        self.vScrollbar.pack(side="left", fill="y")
        self.frame.pack(fill="both", expand=True)
        self.canvas.create_window(
            (4, 4), window=self.frame, anchor="center", tags="self.frame"
        )
        self.canvas.pack(fill="both", expand=True)

        self.frame.bind("<Configure>", self.onFrameConfigure)
        self.responses = []

    def onFrameConfigure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
