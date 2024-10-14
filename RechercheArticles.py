from Article import Article
from Constants import LIGHT2
from GrandeFenetre import GrandeFenetre
import tkinter as tk
from PIL import Image, ImageTk

from outils import call_article_link, from_rgb_to_tkcolors, translate_it


class RechercheArticles:
    status: bool
    total_results: int
    articles: list[Article]

    def __init__(
        self, status: bool, total_results: int, articles: list[Article]
    ) -> None:
        self.status = status
        self.total_results = total_results
        self.articles = articles

    def get_instance(self):
        return GrandeFenetre()

    async def insert_content(self, motcles: str, grande_fenetre: GrandeFenetre):
        """
        récupère contenus images et liens et remplie la grande fenetre
        contenant les informations
        """
        _a = grande_fenetre.area_info
        _a.insert_markdown(mkd_text=(f"# Actus: {motcles}"))
        for n, article in enumerate(self.articles):
            _a.tag_bind("hyperlink", "<Button-1>", call_article_link(url=article.url))
            _a.insert(tk.END, f"Visitez :: {article.url[:30]}...", "hyperlink")
            _a.insert_markdown(f"\n## :: {n+1} :: {translate_it(article.title)}\n")
            _a.insert_markdown(
                f"CreatedAt: Date de publication:: {translate_it(article.published_at)}"
            )
            _a.insert_markdown(
                f"**Description::** {translate_it(article.description)}\n"
            )
            if isinstance(article.image, ImageTk.PhotoImage):
                # Insérer le Canvas dans le widget Text
                img = article.image
                canvas = tk.Canvas(_a, width=img.width(), height=img.height())
                canvas.create_image(0, 0, anchor="nw", image=img)
                canvas.create_rectangle(
                    0,
                    0,
                    img.width(),
                    img.height(),
                    outline=from_rgb_to_tkcolors(LIGHT2),
                    width=2,
                )
                _a.window_create(tk.END, window=canvas, padx=10, pady=10)
            else:
                _a.insert_markdown(f"**aucuneImage** {article.url_to_image}")

            _a.insert_markdown(f"\n**Contenu::** {translate_it(article.content)}")
            _a.insert_markdown(f"**Auteur::** {translate_it(article.author)}**\n")
