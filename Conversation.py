import tkinter as tk

from Lecture import Lecture
from outils import askToAi, from_rgb_to_tkColors, lire_haute_voix
from Constants import DARK1, DARK2, DARK3, LIGHT1, LIGHT2, LIGHT3, ZEFONT
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
        self.fontdict = font.Font(
            family=ZEFONT[0],
            size=ZEFONT[1],
            slant=ZEFONT[2],
            weight=ZEFONT[3],
        )

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=8)
        self.fenexport = None
        self.grande_fenetre = None
        self.submit = submit
        super().__init__(master)
        self.master = master
        self.agent_appel = agent_appel
        self.model_to_use = model_to_use
        self.pack(expand=False)
        self.title = "title"
        self.ai_response = ai_response
        self.canvas_edition = tk.Canvas(
            master=master,
            relief="sunken",
        )

        self.boutons_cnv_response = tk.Frame(self.canvas_edition)
        self.cnv_globals_responses = tk.Frame(self.canvas_edition)
        self.cnv_response = tk.Frame(self.cnv_globals_responses, relief="sunken")
        self.cnv_question = tk.Frame(self.cnv_globals_responses, relief="sunken")

        self.entree_question = SimpleMarkdownText(self.cnv_question, font=default_font)
        self.entree_question.insert_markdown(text)

        self.bouton_supprimer_question_response = tk.Button(
            self.boutons_cnv_response,
            text=" X ",
            command=self.supprimer_conversation,
        )

        self.bouton_supprimer_question_response.configure(
            bg=from_rgb_to_tkColors(DARK2), fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.bouton_supprimer_question_response.pack(side="left")

        self.bouton_maximize_me = tk.Button(
            self.boutons_cnv_response, text=" + ", command=self.maximize_me
        )
        self.bouton_maximize_me.configure(
            bg=from_rgb_to_tkColors(DARK2), fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.bouton_agrandir_fenetre = tk.Button(
            self.boutons_cnv_response, text=" O ", command=self.agrandir_fenetre
        )
        self.bouton_agrandir_fenetre.configure(
            bg=from_rgb_to_tkColors(DARK2), fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.bouton_maximize_me.pack(side="left")
        self.bouton_agrandir_fenetre.pack(side="left")
        self.bouton_normalize_me = tk.Button(
            self.boutons_cnv_response, text=" || ", command=self.normalize_me
        )
        self.bouton_normalize_me.configure(
            bg=from_rgb_to_tkColors(DARK2), fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.bouton_normalize_me.pack(side="left")

        self.bouton_minimize_me = tk.Button(
            self.boutons_cnv_response, text=" - ", command=self.minimize_me
        )
        self.bouton_minimize_me.configure(
            bg=from_rgb_to_tkColors(DARK2), fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.bouton_minimize_me.pack(side="left")

        self.boutton_effacer_entree_response = tk.Button(
            self.boutons_cnv_response,
            text="Effacer",
            command=self.clear_entree_response,
        )

        self.boutton_effacer_entree_response.configure(
            bg=from_rgb_to_tkColors(DARK2), fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.boutton_effacer_entree_response.pack(side="right")

        self.bouton_lire_responses = tk.Button(
            self.boutons_cnv_response,
            text="Lire",
            command=lambda: self.lire_text_from_object(self.entree_response),
        )
        self.bouton_lire_responses.configure(
            bg=from_rgb_to_tkColors(DARK3), fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.bouton_lire_responses.pack(side=tk.RIGHT)

        self.canvas_edition.pack(fill="y", expand=True)
        self.boutons_cnv_response.pack(fill="x", expand=False)

        self.cnv_globals_responses.pack(fill="x", expand=False)
        self.cnv_response.pack(fill="x", expand=False)
        self.cnv_question.pack(fill="x", expand=False)

        self.bouton_transfere = tk.Button(
            self.boutons_cnv_response,
            text="Transférer",
            command=self.transferer,
            bg=from_rgb_to_tkColors(LIGHT1),
            fg=from_rgb_to_tkColors(DARK3),
        )
        self.bouton_transfere.pack(side=tk.RIGHT, fill="both")
        scrollbar_response = tk.Scrollbar(self.cnv_response)
        scrollbar_response.pack(side=tk.RIGHT, fill="both")
        scrollbar_question = tk.Scrollbar(self.cnv_question)
        scrollbar_question.pack(side=tk.RIGHT, fill="both")

        self.entree_response = SimpleMarkdownText(self.cnv_response, font=default_font)
        self.entree_response.configure(
            bg=from_rgb_to_tkColors(LIGHT3),
            fg=from_rgb_to_tkColors(DARK1),
            height=1,
            width=100,
            font=self.fontdict,
            wrap="word",
            padx=10,
            pady=6,
            yscrollcommand=scrollbar_response.set,
        )
        # self.entree_question = SimpleMarkdownText(
        #     self.cnv_question, height=1, font=default_font
        # )
        self.entree_question.configure(
            bg=from_rgb_to_tkColors(LIGHT2),
            fg=from_rgb_to_tkColors(DARK3),
            height=4,
            width=100,
            wrap="word",
            padx=10,
            pady=6,
            yscrollcommand=scrollbar_question.set,
        )
        self.entree_question.bind("<Control-Return>", func=lambda: self.submit())
        self.entree_response.pack(fill="both", expand=False)
        self.entree_question.pack(fill="both", expand=False)

        scrollbar_response.configure(
            command=self.entree_response.yview, bg=from_rgb_to_tkColors(DARK2)
        )
        scrollbar_question.configure(
            command=self.entree_question.yview, bg=from_rgb_to_tkColors(DARK2)
        )

    def supprimer_conversation(self):
        # TODO : supprimer la covnersation visuellement mais aussi dans la liste des conversations
        self.canvas_edition.destroy()
        self.destroy()

        pass

    def transferer(self):
        try:
            content = self.get_entree_response().get(tk.SEL_FIRST, tk.SEL_LAST)
            self.entree_question.insert_markdown(content)
        except:
            (
                self.entree_question.insert_markdown(
                    self.get_entree_response().get_text()
                )
                if self.get_entree_response().get_text() != ""
                else print("Oups, il n'y a rien à transférer")
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
            height=int(self.entree_response.cget("height")) + 10, width=100
        )
        self.entree_question.configure(height=10, width=100)

        self.entree_question.pack_propagate()
        self.entree_response.pack_propagate()

    def agrandir_fenetre(self):
        self.affiche_fenetre_agrandie()

    def affiche_fenetre_agrandie(self):
        self.fenexport = tk.Tk()
        self.fenexport.geometry("600x900")
        self.fenexport.title(self.entree_question.get_text()[:20] + "...")

        self.boutlire = tk.Button(
            self.fenexport,
            text="Lire",
            command=lambda: self.lire_text_from_object(self.grande_fenetre),
        )
        self.boutlire.pack(fill="x", expand=False)
        self.grande_fenetre = SimpleMarkdownText(self.fenexport)
        self.grande_fenetre.configure(
            wrap="word", bg=from_rgb_to_tkColors(LIGHT3), fg=from_rgb_to_tkColors(DARK3)
        )

        self.grande_fenetre.configure(font=self.fontdict)
        self.grande_fenetre.tag_configure(
            tagName="boldtext",
            font=font.Font(
                family=self.fontdict.cget("family"),
                size=self.fontdict.cget("size"),
                slant=self.fontdict.cget("slant"),
                weight="bold",
            ),
        )
        #
        self.grande_fenetre.tag_configure(
            tagName="response",
            border=20,
            wrap="word",
            spacing1=10,
            spacing3=10,
            lmargin1=10,
            lmargin2=10,
            lmargincolor="green",
            rmargin=10,
            rmargincolor="green",
            selectbackground="red",
        )
        self.grande_fenetre.tag_configure(
            tagName="balise",
            font=self.fontdict,
            foreground=from_rgb_to_tkColors((0, 0, 250)),
            # foreground=from_rgb_to_tkColors((100, 100, 100)),
        )

        self.grande_fenetre.tag_configure(
            tagName="balise_bold",
            font=font.Font(
                family=self.fontdict.cget("family"),
                size=self.fontdict.cget("size"),
                slant=self.fontdict.cget("slant"),
                weight="bold",
            ),
            foreground=from_rgb_to_tkColors((100, 100, 100)),
        )

        self.grande_fenetre.insert_markdown(self.get_ai_response())

        self.grande_fenetre.pack(fill="both", expand=True)
        self.grande_fenetre.configure(width=100)
        self.fenexport.mainloop()

    def normalize_me(self):
        self.entree_response.configure(height=1, width=100)
        self.entree_question.configure(height=1, width=100)
        self.entree_question.pack_propagate()
        self.entree_response.pack_propagate()

    def minimize_me(self):
        self.entree_response.configure(
            height=int(self.entree_response.cget("height")) - 5, width=100
        )
        self.entree_question.configure(height=0, width=100)
        self.entree_response.pack_propagate()
        self.entree_question.pack_propagate()

    def set_ai_response(self, response):
        self.ai_response = response

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

    def lire_text_from_object(self, object: SimpleMarkdownText):
        try:
            texte_to_talk = object.get(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            texte_to_talk = object.get("1.0", tk.END)
        finally:
            Lecture(text=texte_to_talk).read()
            # lancement_de_la_lecture(texte_to_talk)
