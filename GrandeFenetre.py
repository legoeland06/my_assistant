import tkinter as tk
from tkinter import font
from tkinter import simpledialog
from Constants import DARK2, LIGHT2, ZEFONT
from PdfMaker import makePdfFromTtext
from SimpleMarkdownText import SimpleMarkdownText
from outils import from_rgb_to_tkColors, lire_text_from_object,  reformateText


class GrandeFenetre(tk.Toplevel):
    images:list
    links:list

    def __init__(self,*args, **kwargs):
        """
        construit une grande fenetre qui va recevoir les informations d'actualités
        """
        super().__init__(*args, **kwargs)
        
        self.fontConversation = font.Font(
            family=ZEFONT[0],
            size=ZEFONT[1],
            slant=ZEFONT[2],
            weight=ZEFONT[3],
        )


        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(size=8)
        self.btn_font = font.nametofont("TkIconFont")
        self.btn_font.configure(size=14)

        self.frame_of_cnv = tk.Frame(self)
        self.frame_of_cnv.pack(side="top", fill="x")

        self.boutlire = tk.Button(
            self.frame_of_cnv,
            font=font.Font(size=self.btn_font.cget("size") + 4),
            fg="green",
            text="▶",
            command=lambda: lire_text_from_object(self.area_info),
        )
        self.bout_diminue = tk.Button(
            self.frame_of_cnv,
            fg="blue",
            font=font.Font(size=self.btn_font.cget("size") + 4),
            text="α",
            command=self.diminue,
        )
        self.bout_augmente = tk.Button(
            self.frame_of_cnv,
            fg="blue",
            font=font.Font(size=self.btn_font.cget("size") + 4),
            text="Α",
            command=self.augmente,
        )
        self.bout_ok = tk.Button(
            self.frame_of_cnv,
            fg="green",
            font=font.Font(size=self.btn_font.cget("size") + 4),
            text="🆗",
            command=self.create_pdf,
        )

        self.bout_augmente.pack(side="left")
        self.bout_diminue.pack(side="left")
        self.boutlire.pack(side="left", expand=False)
        self.bout_ok.pack(side="left")

        self.area_info = SimpleMarkdownText(
            self,
            font=self.fontConversation,
            bg=from_rgb_to_tkColors(DARK2),
            fg=from_rgb_to_tkColors(LIGHT2),
            wrap="word",
            
        )

        self.scrlbar = tk.Scrollbar(self)
        self.scrlbar.pack(side=tk.RIGHT, fill="both")

        self.area_info.configure(padx=20,pady=10,yscrollcommand=self.scrlbar.set)
        self.scrlbar.configure(
            command=self.area_info.yview, bg=from_rgb_to_tkColors(DARK2)
        )
        self.area_info.pack(fill="both",expand=True)

    def augmente(self):
        self.fontConversation.configure(size=(self.fontConversation.cget("size") + 2))

    def diminue(self):
        self.fontConversation.configure(size=(self.fontConversation.cget("size") - 2))

    def create_pdf(self):
        makePdfFromTtext(
            filename=(
                simpledialog.askstring(
                    parent=self,
                    prompt="Enregistrement : veuillez choisir un nom au fichier",
                    title="Enregistrer vers pdf",
                )
                or "myPdf"
            ),
            text_list=reformateText(
                (
                    self.area_info.get_text()
                    if not self.area_info is None
                    else "texte vide"
                ),
                n=115,
            ),
        )
