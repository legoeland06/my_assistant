from Article import Article
from Constants import LIGHT2
from GrandeFenetre import GrandeFenetre
import tkinter as tk
from PIL import Image,ImageTk

from outils import callback, from_rgb_to_tkColors, translate_it

class RechercheArticles():
    status:bool
    totalResults:int
    articles:list[Article]

    def __init__(self,status:bool,totalResults:int,articles:list[Article]) -> None:
        self.status=status
        self.totalResults=totalResults
        self.articles=articles
            
    def initGrandeFenetre(self):
        return GrandeFenetre()

    async def insertContentToGrandeFentre(self, motcles:str):
        """
        récupère contenus images et liens et remplie la grande fenetre
        contenant les informations
        """
        grandeFenetre=self.initGrandeFenetre()
        grandeFenetre.area_info.insert_markdown(mkd_text=(f"# Actus: {motcles}"))
        for n,article in enumerate(self.articles):
            grandeFenetre.area_info.tag_config("hyperlink", foreground="yellow", underline=True)
            grandeFenetre.area_info.tag_bind("hyperlink", "<Button-1>", lambda e: callback(article.url))
            grandeFenetre.area_info.insert(tk.END,f"Visitez :: {article.url[:30]}...","hyperlink")
            grandeFenetre.area_info.insert_markdown(f"\n")
            grandeFenetre.area_info.insert_markdown(f"## :: {n+1} :: {translate_it(article.title)}")
            grandeFenetre.area_info.insert_markdown(f"\n")
            grandeFenetre.area_info.insert_markdown(f"**Date de publication::** {translate_it(article.publishedAt)}")
            grandeFenetre.area_info.insert_markdown(f"**Description::** {translate_it(article.description)}")
            grandeFenetre.area_info.insert_markdown(f"\n")
            if isinstance(article.image,ImageTk.PhotoImage):
                # Insérer le Canvas dans le widget Text
                img=article.image
                canvas=tk.Canvas(grandeFenetre.area_info, width=img.width(), height=img.height())
                canvas.create_image(0, 0, anchor="nw", image=img)
                canvas.create_rectangle(0, 0, img.width(), img.height(), outline=from_rgb_to_tkColors(LIGHT2), width=2)
                grandeFenetre.area_info.window_create(tk.END, window=canvas,padx=10,pady=10)
            else:
                grandeFenetre.area_info.insert_markdown(f"**aucuneImage** {article.urlToImage}")

            grandeFenetre.area_info.insert_markdown(f"\n")
            grandeFenetre.area_info.insert_markdown(f"**Contenu::** {translate_it(article.content)}")
            grandeFenetre.area_info.insert_markdown(f"**Auteur::** {translate_it(article.author)}**")
            grandeFenetre.area_info.insert_markdown(f"\n")
        