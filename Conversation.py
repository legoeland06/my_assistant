import tkinter as tk
from tkinter import simpledialog

from GrandeFenetre import GrandeFenetre
from PdfMaker import make_pdf_from_text
from outils import (
    from_rgb_to_tkcolors,
    lire,
    lire_text_from_object,
    reformat_text,
)
from Constants import DARK2, DARK3, LIGHT1, LIGHT2, LIGHT3, ZEFONT
from SimpleMarkdownText import SimpleMarkdownText

from tkinter import font


class Conversation(tk.Frame):
    """
    affiche une frame constituée de deux frames
    * response
    * question

    cette classe devrait être appelée à chaque
    validarion de prompt principal pour afficher
    le prompt et le résultat attendu
    """

    id: str
    grande_fenetre: GrandeFenetre

    def __init__(
        self,
        master: tk.Frame,
        text: str,
        ai_response: str,
        submit,
        agent_appel,
        model_to_use,
        nb_conversation: int,
    ):
        super().__init__(master)
        self.fontdict = font.Font(
            family=ZEFONT[0],
            size=ZEFONT[1],
            slant=ZEFONT[2],
            weight=ZEFONT[3],
        )

        self.nb_conversation = nb_conversation
        self.fontConversation = font.Font(
            family=ZEFONT[0],
            size=ZEFONT[1],
            slant=ZEFONT[2],
            weight=ZEFONT[3],
        )
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(size=14)
        self.btn_font = font.nametofont("TkIconFont")
        self.btn_font.configure(size=14)

        self.fenexport = None
        self.submit = submit
        self.agent_appel = agent_appel
        self.model_to_use = model_to_use

        self.title = "title"
        self.ai_response = ai_response
        self.canvas_edition = tk.Canvas(
            master=master,
            relief="flat",
        )
        self.canvas_edition.pack(fill="x", expand=True)

        self.canvas_boutons_conversation = tk.Frame(self.canvas_edition)
        self.cnv_global_conversation = tk.Frame(self.canvas_edition)
        self.cnv_response = tk.Frame(self.cnv_global_conversation, relief="flat")
        self.cnv_question = tk.Frame(self.cnv_global_conversation, relief="flat")

        self.entree_question = SimpleMarkdownText(
            self.cnv_question, font=self.default_font
        )
        self.entree_question.insert_markdown(text)

        self.bouton_supprimer_question_response = tk.Button(
            self.canvas_boutons_conversation,
            font=self.btn_font,
            text="❌",
            command=self.supprimer_conversation,
        )

        self.bouton_supprimer_question_response.configure(
            bg=from_rgb_to_tkcolors(DARK2), fg=from_rgb_to_tkcolors(LIGHT3)
        )
        self.bouton_supprimer_question_response.pack(side="left")

        self.bouton_maximize_me = tk.Button(
            self.canvas_boutons_conversation,
            font=self.btn_font,
            text="⬆",
            command=self.maximize_me,
        )
        self.bouton_maximize_me.configure(
            bg=from_rgb_to_tkcolors(DARK2), fg=from_rgb_to_tkcolors(LIGHT3)
        )
        self.bouton_agrandir_fenetre = tk.Button(
            self.canvas_boutons_conversation,
            font=self.btn_font,
            text="➕",
            command=self.affiche_fenetre_agrandie,
        )
        self.bouton_agrandir_fenetre.configure(
            bg=from_rgb_to_tkcolors(DARK2), fg=from_rgb_to_tkcolors(LIGHT3)
        )
        self.bouton_maximize_me.pack(side="left")
        self.bouton_agrandir_fenetre.pack(side="left")
        self.bouton_normalize_me = tk.Button(
            self.canvas_boutons_conversation,
            font=self.btn_font,
            text="➖",
            command=self.normalize_me,
        )
        self.bouton_normalize_me.configure(
            bg=from_rgb_to_tkcolors(DARK2), fg=from_rgb_to_tkcolors(LIGHT3)
        )
        self.bouton_normalize_me.pack(side="left")

        self.bouton_minimize_me = tk.Button(
            self.canvas_boutons_conversation,
            font=self.btn_font,
            text="⬇",
            command=self.minimize_me,
        )
        self.bouton_minimize_me.configure(
            bg=from_rgb_to_tkcolors(DARK2), fg=from_rgb_to_tkcolors(LIGHT3)
        )
        self.bouton_minimize_me.pack(side="left")

        self.boutton_effacer_contenu = tk.Button(
            self.canvas_boutons_conversation,
            font=self.btn_font,
            text="⭕",
            command=self.clear_entree_response,
        )

        self.boutton_effacer_contenu.configure(
            bg=from_rgb_to_tkcolors(DARK2), fg=from_rgb_to_tkcolors(LIGHT3)
        )
        self.boutton_effacer_contenu.pack(side="right")

        self.bouton_lire_conversation = tk.Button(
            self.canvas_boutons_conversation,
            font=self.btn_font,
            text="▶",
            command=lambda: lire_text_from_object(self.entree_response),
        )
        self.bouton_lire_conversation.configure(
            bg=from_rgb_to_tkcolors(DARK3), fg=from_rgb_to_tkcolors(LIGHT3)
        )
        self.bouton_lire_conversation.pack(side=tk.RIGHT)

        self.canvas_boutons_conversation.pack(fill="x", expand=True)

        self.cnv_global_conversation.pack()
        self.cnv_response.pack()
        self.cnv_question.pack()

        self.bouton_transfere = tk.Button(
            self.canvas_boutons_conversation,
            font=self.btn_font,
            text="🔀",
            command=self.transferer,
            bg=from_rgb_to_tkcolors(LIGHT1),
            fg=from_rgb_to_tkcolors(DARK3),
        )
        self.bouton_transfere.pack(side=tk.RIGHT, fill="both")
        scrollbar_response = tk.Scrollbar(self.cnv_response)
        scrollbar_response.pack(side=tk.RIGHT, fill="both")
        scrollbar_question = tk.Scrollbar(self.cnv_question)
        scrollbar_question.pack(side=tk.RIGHT, fill="both")

        self.entree_response = SimpleMarkdownText(
            self.cnv_response,
            font=self.default_font,
        )
        self.entree_response.configure(
            bg=from_rgb_to_tkcolors(LIGHT3),
            fg=from_rgb_to_tkcolors((0, 0, 153)),
            height=3,
            width=100,
            wrap="word",
            pady=6,
            padx=6,
            yscrollcommand=scrollbar_response.set,
            startline=4,
            undo=True,
        )

        self.entree_question.configure(
            bg=from_rgb_to_tkcolors(LIGHT2),
            fg=from_rgb_to_tkcolors((128, 0, 0)),
            height=4,
            width=100,
            wrap="word",
            pady=6,
            padx=6,
            yscrollcommand=scrollbar_question.set,
        )

        self.entree_response.pack(fill="x", expand=True)
        self.entree_question.pack(fill="x", expand=True)

        scrollbar_response.configure(
            command=self.entree_response.yview, bg=from_rgb_to_tkcolors(DARK2)
        )
        scrollbar_question.configure(
            command=self.entree_question.yview, bg=from_rgb_to_tkcolors(DARK2)
        )

        self.id = str(self.__str__())

    def supprimer_conversation(self):
        self.destroy()
        self.canvas_edition.destroy()

    def transferer(self):
        self.get_entree_response().tag_add("sel", "1.0", "end")
        self.get_entree_response().clipboard_clear()
        self.get_entree_response().clipboard_append(
            self.get_entree_response().get_text()
        )

    def maximize_me(self):
        self.entree_response.configure(
            height=int(self.entree_response.cget("height")) + 10,
        )
        self.entree_question.configure(
            height=10,
        )

    def augmente(self):
        self.fontConversation.configure(size=(self.fontConversation.cget("size") + 2))

    def diminue(self):
        self.fontConversation.configure(size=(self.fontConversation.cget("size") - 2))

    def create_pdf(self):
        make_pdf_from_text(
            filename=(
                simpledialog.askstring(
                    parent=self.master,
                    prompt="Enregistrement : veuillez choisir un nom au fichier",
                    title="Enregistrer vers pdf",
                )
                or "myPdf"
            ),
            text_list=reformat_text(
                (
                    self.grande_fenetre.area_info.get_text()
                    if self.grande_fenetre is not None
                    else "texte vide"
                ),
                n=115,
            ),
        )

    def affiche_fenetre_agrandie(self):
        self.grande_fenetre = GrandeFenetre(tk.Toplevel(name=self.widgetName))
        self.grande_fenetre.area_info.configure(
            bg=from_rgb_to_tkcolors((0x01, 0x2A, 0x4A))
        )
        self.grande_fenetre.area_info.insert_markdown(self.get_ai_response())

    def normalize_me(self):
        self.entree_response.configure(
            height=1,
        )
        self.entree_question.configure(
            height=1,
        )

    def minimize_me(self):
        self.entree_response.configure(
            height=int(self.entree_response.cget("height")) - 5,
        )
        self.entree_question.configure(
            height=0,
        )

    def get_ai_response(self) -> str:
        return self.ai_response

    def get_entree_response(self) -> SimpleMarkdownText:
        return self.entree_response

    def set_entree_response(self, response: SimpleMarkdownText):
        self.entree_response = response

    def get_entree_question(self) -> SimpleMarkdownText:
        return self.entree_question

    def set_entree_question(self, question: SimpleMarkdownText):
        self.entree_question = question

    def clear_entree_response(self):
        self.entree_response.clear_text()
        self.entree_question.clear_text()

    def lire(self):
        lire(
            f"Conversation numéro: {self.nb_conversation} \n"
            + self.entree_response.get_text()
        )
