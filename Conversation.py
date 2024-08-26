import tkinter as tk
from tkinter import simpledialog

from PdfMaker import makePdfFromTtext
from outils import (
    askToAi,
    from_rgb_to_tkColors,
    lire_haute_voix,
    splittextintochunks,
)
from Constants import DARK2, DARK3, LIGHT1, LIGHT2, LIGHT3, ZEFONT
from SimpleMarkdownText import SimpleMarkdownText

# import tkinter.font as tkfont
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

    id:str
    def __init__(
        self,
        master: tk.Frame,
        # TODO : passer plutot une str au lieu de l'objet
        text: str,
        ai_response: str,
        submit,
        agent_appel,
        model_to_use,
    ):
        super().__init__(master)
        self.fontdict = font.Font(
            family=ZEFONT[0],
            size=ZEFONT[1],
            slant=ZEFONT[2],
            weight=ZEFONT[3],
        )

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

        self.fenexport = None
        self.grande_fenetre = SimpleMarkdownText()
        self.submit = submit
        self.agent_appel = agent_appel
        self.model_to_use = model_to_use

        # TODO: avoir avec true ou inexistant
        # self.pack(fill="both",expand=True)

        self.title = "title"
        self.ai_response = ai_response
        self.canvas_edition = tk.Canvas(
            master=master,
            relief="flat",
        )
        self.canvas_edition.pack(fill="both", expand=True)

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
            bg=from_rgb_to_tkColors(DARK2), fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.bouton_supprimer_question_response.pack(side="left")

        self.bouton_maximize_me = tk.Button(
            self.canvas_boutons_conversation,
            font=self.btn_font,
            text="⬆",
            command=self.maximize_me,
        )
        self.bouton_maximize_me.configure(
            bg=from_rgb_to_tkColors(DARK2), fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.bouton_agrandir_fenetre = tk.Button(
            self.canvas_boutons_conversation,
            font=self.btn_font,
            text="➕",
            command=self.agrandir_fenetre,
        )
        self.bouton_agrandir_fenetre.configure(
            bg=from_rgb_to_tkColors(DARK2), fg=from_rgb_to_tkColors(LIGHT3)
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
            bg=from_rgb_to_tkColors(DARK2), fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.bouton_normalize_me.pack(side="left")

        self.bouton_minimize_me = tk.Button(
            self.canvas_boutons_conversation,
            font=self.btn_font,
            text="⬇",
            command=self.minimize_me,
        )
        self.bouton_minimize_me.configure(
            bg=from_rgb_to_tkColors(DARK2), fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.bouton_minimize_me.pack(side="left")

        self.boutton_effacer_contenu = tk.Button(
            self.canvas_boutons_conversation,
            font=self.btn_font,
            text="⭕",
            command=self.clear_entree_response,
        )

        self.boutton_effacer_contenu.configure(
            bg=from_rgb_to_tkColors(DARK2), fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.boutton_effacer_contenu.pack(side="right")

        self.bouton_lire_conversation = tk.Button(
            self.canvas_boutons_conversation,
            font=self.btn_font,
            text="▶",
            command=lambda: self.lire_text_from_object(self.entree_response),
        )
        self.bouton_lire_conversation.configure(
            bg=from_rgb_to_tkColors(DARK3), fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.bouton_lire_conversation.pack(side=tk.RIGHT)

        self.canvas_boutons_conversation.pack(fill="x", expand=True)

        self.cnv_global_conversation.pack(fill="both", expand=True)
        self.cnv_response.pack(fill="x", expand=True)
        self.cnv_question.pack(fill="x", expand=True)

        self.bouton_transfere = tk.Button(
            self.canvas_boutons_conversation,
            font=self.btn_font,
            text="🔀",
            command=self.transferer,
            bg=from_rgb_to_tkColors(LIGHT1),
            fg=from_rgb_to_tkColors(DARK3),
        )
        self.bouton_transfere.pack(side=tk.RIGHT, fill="both")
        scrollbar_response = tk.Scrollbar(self.cnv_response)
        scrollbar_response.pack(side=tk.RIGHT, fill="both")
        scrollbar_question = tk.Scrollbar(self.cnv_question)
        scrollbar_question.pack(side=tk.RIGHT, fill="both")

        self.entree_response = SimpleMarkdownText(
            self.cnv_response, font=self.default_font
        )
        self.entree_response.configure(
            bg=from_rgb_to_tkColors(LIGHT3),
            fg=from_rgb_to_tkColors((0,0,153)),
            height=1,
            width=125,
            wrap="word",
            pady=6,
            yscrollcommand=scrollbar_response.set,
        )

        self.entree_question.configure(
            bg=from_rgb_to_tkColors(LIGHT2),
            fg=from_rgb_to_tkColors((128,0,0)),
            height=4,
            width=125,
            wrap="word",
            pady=6,
            yscrollcommand=scrollbar_question.set,
        )
        self.entree_question.bind("<Control-Return>", func=lambda: self.submit())  # type: ignore
        self.entree_response.pack(fill="both", expand=True)
        self.entree_question.pack(fill="both", expand=True)

        scrollbar_response.configure(
            command=self.entree_response.yview, bg=from_rgb_to_tkColors(DARK2)
        )
        scrollbar_question.configure(
            command=self.entree_question.yview, bg=from_rgb_to_tkColors(DARK2)
        )

        self.id=str(self.__str__())

    def supprimer_conversation(self):
        self.destroy()
        self.canvas_edition.destroy()
        

    def transferer(self):
        self.get_entree_response().tag_add("sel", "1.0", "end")
        self.get_entree_response().clipboard_clear()
        self.get_entree_response().clipboard_append(
            self.get_entree_response().get_text()
        )

    def submission(self, evt):
        submission_texte = self.entree_question.get_text()
        response_ai, _timing = askToAi(
            agent_appel=self.agent_appel,
            prompt=submission_texte,
            model_to_use=self.model_to_use,
        )
        self.entree_response.insert_markdown(response_ai)

    def maximize_me(self):
        self.entree_response.configure(
            height=int(self.entree_response.cget("height")) + 10,
        )
        self.entree_question.configure(
            height=10,
        )

    def agrandir_fenetre(self):
        self.affiche_fenetre_agrandie()

    def augmente(self):
        self.fontConversation.configure(size=(self.fontConversation.cget("size") + 2))

    def diminue(self):
        self.fontConversation.configure(size=(self.fontConversation.cget("size") - 2))

    def create_pdf(self):
        makePdfFromTtext(
            filename=(
                simpledialog.askstring(
                    parent=self.master,
                    prompt="Enregistrement : veuillez choisir un nom au fichier",
                    title="Enregistrer vers pdf",
                )
                or "myPdf"
            ),
            text_list=self.reformateText(
                (
                    self.grande_fenetre.get_text()
                    if not self.grande_fenetre is None
                    else "texte vide"
                ),
                n=115,
            ),
        )

    def reformateText(self, text: str, n: int) -> list[str]:
        reservoir = []
        for line in text.splitlines():
            if len(line) > n:
                reservoir.extend(splittextintochunks(line, n))
            else:
                reservoir.append(line)
        return reservoir

    def affiche_fenetre_agrandie(self):
        self.fenexport = tk.Toplevel()
        # self.fenexport.geometry("600x900")
        self.fenexport.title(self.widgetName)
        self.canvas_buttons = tk.Canvas(self.fenexport)
        self.canvas_buttons.pack(side="top")

        self.grande_fenetre.master=self.fenexport
        self.boutlire = tk.Button(
            self.canvas_buttons,
            font=self.btn_font,
            fg="green",
            text="▶",
            command=lambda: self.lire_text_from_object(self.grande_fenetre),
        )
        self.bout_diminue = tk.Button(
            self.canvas_buttons,
            fg="blue",
            font=self.btn_font,
            text="α",
            command=self.diminue,  
        )
        self.bout_augmente = tk.Button(
            self.canvas_buttons,
            fg="blue",
            font=self.btn_font,
            text="Α",
            command=self.augmente,  
        )
        self.bout_ok = tk.Button(
            self.canvas_buttons,
            fg="green",
            font=self.btn_font,
            text="🆗",
            command=self.create_pdf,  
        )

        self.bout_ok.pack(side="right")
        self.bout_diminue.pack(side="left")
        self.bout_augmente.pack(side="left")
        self.boutlire.pack(side="left", expand=False)
        self.grande_fenetre.configure(
            font=self.fontConversation,
            wrap="word",
            bg=from_rgb_to_tkColors((28,0,0)),
            fg=from_rgb_to_tkColors(
                LIGHT2,
            ),
        )

        self.grande_fenetre.insert_markdown(self.get_ai_response())

        self.grande_fenetre.pack(fill="both",expand=True)

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
        lire_haute_voix(self.entree_response.get_text())

    def lire_text_from_object(self, object: SimpleMarkdownText):
        try:
            texte_to_talk = object.get(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            texte_to_talk = object.get("1.0", tk.END)
        finally:
            lire_haute_voix(texte_to_talk)
