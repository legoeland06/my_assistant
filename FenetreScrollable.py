import tkinter as tk
from Constants import LIGHT0
from outils import (
    from_rgb_to_tkcolors,
)


class FenetreScrollable(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.canvas = tk.Canvas(
            self,
            borderwidth=0,
            background=from_rgb_to_tkcolors(LIGHT0),
            relief="flat",
        )
        self.canvas.pack(fill="both", expand=True)

        self.frame = tk.Frame(
            self.canvas,
            background=from_rgb_to_tkcolors(LIGHT0),
        )
        self.bind("<Configure>", self.onFrameConfigure)
        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.vScrollbar = tk.Scrollbar(
            self.master, orient="vertical", command=self.canvas.yview
        )
        self.vScrollbar.pack(side="left", fill="y")
        self.frame.pack(fill="both", expand=True)

        self.canvas.configure(yscrollcommand=self.vScrollbar.set)

        self.canvas.create_window(
            (4, 4), window=self.frame, anchor="center", tags="self.frame"
        )

        self.pack(fill="both", expand=True)

    def onFrameConfigure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
