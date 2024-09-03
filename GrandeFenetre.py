import time
import tkinter as tk
from tkinter import PhotoImage, font
from tkinter import simpledialog
from typing import Any


from Constants import DARK2, LIGHT2, ZEFONT
from PdfMaker import makePdfFromTtext
from SimpleMarkdownText import SimpleMarkdownText
from outils import callback, downloadimage, from_rgb_to_tkColors, lire_text_from_object,  reformateText, translate_it


class GrandeFenetre(tk.Toplevel):
    def __init__(self,*args, **kwargs):
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
        self.btn_font.configure(size=8)

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


        # _ok=await self.insertContent(content)

    async def insertContent(self, content,images:list,tags:list):
        self.images=images
        self.tags=tags
        self.area_info.insert_markdown(mkd_text=(f"# Actualités"))
        n=0
        for article in content:
            if n>19:
                break
            self.area_info.tag_config("hyperlink", foreground="yellow", underline=True)
            self.area_info.tag_bind("hyperlink", "<Button-1>", lambda e: callback(self.tags.__getitem__(n)))
            self.area_info.insert(tk.END,f"## {n} Visitez :: {self.tags.__getitem__(n)[:30]}...","hyperlink")
            self.area_info.insert_markdown(f"\n")
            self.area_info.insert_markdown(f"## {n} :: {translate_it(article["title"])}")
            self.area_info.insert_markdown(f"\n")
            self.area_info.insert_markdown(f"**Date de publication::** {translate_it(article["publishedAt"])}")
            self.area_info.insert_markdown(f"**Description::** {translate_it(article["description"])}")
            self.area_info.insert_markdown(f"\n")
            try:
                # Insérer le Canvas dans le widget Text
                img=self.images.__getitem__(n)
                canvas=tk.Canvas(self.area_info, width=img.width(), height=img.height())
                canvas.create_image(0, 0, anchor="nw", image=img)
                canvas.create_rectangle(0, 0, img.width(), img.height(), outline=from_rgb_to_tkColors(LIGHT2), width=2)
                self.area_info.window_create(tk.END, window=canvas,padx=10,pady=10)
            except:
                self.area_info.insert_markdown(f"**aucuneImage** {article["urlToImage"]}")
            self.area_info.insert_markdown(f"\n")
            self.area_info.insert_markdown(f"**Contenu::** {translate_it(article["content"])}")
            self.area_info.insert_markdown(f"**Auteur::** {translate_it(article["author"])}**")
            self.area_info.insert_markdown(f"\n")
            n+=1
        return True

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
