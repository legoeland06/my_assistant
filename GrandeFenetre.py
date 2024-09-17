import tkinter as tk
from tkinter import font
from tkinter import simpledialog
from Constants import DARK2, DARK3, LIGHT1, LIGHT2, ZEFONT
from PdfMaker import makePdfFromTtext
from SimpleMarkdownText import SimpleMarkdownText
from outils import from_rgb_to_tkColors, lire_text_from_object, reformateText


class GrandeFenetre(tk.Frame):
    images: list
    links: list

    def __init__(self, *args, **kwargs):
        """
        construit une grande fenetre qui va recevoir les informations d'actualités
        """
        super().__init__(*args, **kwargs)
        self.pack(fill="both", expand=True)

        self.default_font = font.nametofont("TkTextFont")
        self.default_font.configure(size=8)
        self.btn_font = font.nametofont("TkTextFont")
        self.btn_font.configure(size=14)
        self.fontConversation = font.nametofont("TkTextFont")

        self.frame_of_cnv = tk.Frame(self)
        self.frame_of_cnv.pack(side="top", fill="x")

        self.boutQuit = tk.Button(
            self.frame_of_cnv,
            font=font.Font(size=self.btn_font.cget("size") + 4),
            fg="green",
            text="X",
            command=self.quitter,
        )

        self.boutReduire = tk.Button(
            self.frame_of_cnv,
            font=font.Font(size=self.btn_font.cget("size") + 4),
            fg="green",
            text="-",
            command=self.diminueHeight,
        )

        self.boutAugmente = tk.Button(
            self.frame_of_cnv,
            font=font.Font(size=self.btn_font.cget("size") + 4),
            fg="green",
            text="+",
            command=self.augmenteHeight,
        )

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
            command=self.diminue_police,
        )
        self.bout_augmente = tk.Button(
            self.frame_of_cnv,
            fg="blue",
            font=font.Font(size=self.btn_font.cget("size") + 4),
            text="Α",
            command=self.augmente_police,
        )
        self.bout_ok = tk.Button(
            self.frame_of_cnv,
            fg="green",
            font=font.Font(size=self.btn_font.cget("size") + 4),
            text="🆗",
            command=self.create_pdf,
        )

        self.boutton_paste_clipboard = tk.Button(
            self.frame_of_cnv,
            font=font.Font(size=self.btn_font.cget("size") + 4),
            text="✔",
            fg="green",
            command=self.paste_clipboard,
        )

        self.bouton_transfere = tk.Button(
            self.frame_of_cnv,
            font=font.Font(size=self.btn_font.cget("size") + 4),
            text="🔀",
            command=self.transferer,
            bg=from_rgb_to_tkColors(LIGHT1),
            fg=from_rgb_to_tkColors(DARK3),
        )

        self.boutQuit.pack(side="left")
        self.boutReduire.pack(side="left")
        self.boutAugmente.pack(side="left")
        self.bout_augmente.pack(side="left")
        self.bout_diminue.pack(side="left")
        self.boutlire.pack(side="left", expand=False)
        self.bout_ok.pack(side="left")
        self.bouton_transfere.pack(side="left")
        self.boutton_paste_clipboard.pack(side="left")

        self.area_info = SimpleMarkdownText(
            self,
            font=self.fontConversation,
            bg=from_rgb_to_tkColors(DARK2),
            fg=from_rgb_to_tkColors(LIGHT2),
            wrap="word",
        )

        self.scrlbar = tk.Scrollbar(self)
        self.scrlbar.pack(side=tk.RIGHT, fill="both")

        self.area_info.configure(padx=20, pady=10, yscrollcommand=self.scrlbar.set)
        self.scrlbar.configure(
            command=self.area_info.yview, bg=from_rgb_to_tkColors(DARK2)
        )
        self.area_info.pack(fill="both", expand=True)

    def quitter(self):
        self.destroy()

    def augmenteHeight(self):
        self.area_info.configure(height=self.area_info.cget('height')+2)

    def diminueHeight(self):
        self.area_info.configure(height=self.area_info.cget('height')-2)


    def transferer(self):
        self.area_info.tag_add("sel", "1.0", "end")
        self.area_info.clipboard_clear()
        self.area_info.clipboard_append(self.area_info.get_text())

    def paste_clipboard(self):
        self.area_info.clear_text()
        self.area_info.insert_markdown(self.clipboard_get())

    def augmente_police(self):
        self.fontConversation.configure(size=(self.fontConversation.cget("size") + 2))
        self.default_font.configure(size=(self.fontConversation.cget("size") + 2))
        self.btn_font.configure(size=(self.fontConversation.cget("size") + 2))

    def diminue_police(self):
        self.fontConversation.configure(size=(self.fontConversation.cget("size") - 2))
        self.default_font.configure(size=(self.fontConversation.cget("size") - 2))
        self.btn_font.configure(size=(self.fontConversation.cget("size") - 2))

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
