import tkinter as tk
from typing import Any

from outils import askToAi, from_rgb_to_tkColors
from Constants import DARK1, DARK2, DARK3, LIGHT1, LIGHT2, LIGHT3
from SimpleMarkdownText import SimpleMarkdownText
import tkinter.font as tkfont


class FenetreResponse(tk.Frame):
    """
    affiche une frame constituée de deux frames
    * response
    * question

    cette classe devrait être appelée à chaque
    validarion de prompt principal
    """

    def __init__(
        self,
        master: tk.Frame,
        entree_recup: SimpleMarkdownText,
        ai_response: str,
        submit,
        agent_appel,
        model_to_use,
    ):
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
        self.entree_prompt = entree_recup

        self.boutons_cnv_response = tk.Frame(self.canvas_edition)
        self.cnv_globals_responses = tk.Frame(self.canvas_edition)
        self.cnv_response = tk.Frame(self.cnv_globals_responses, relief="sunken")
        self.cnv_question = tk.Frame(self.cnv_globals_responses, relief="sunken")

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
        self.bouton_maximize_me.pack(side="left")

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
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=8)
        self.entree_response = SimpleMarkdownText(self.cnv_response, font=default_font)
        self.entree_response.configure(
            bg=from_rgb_to_tkColors(LIGHT3),
            fg=from_rgb_to_tkColors(DARK1),
            height=5,
            width=100,
            font=("Arial", 12),
            wrap="word",
            padx=10,
            pady=6,
            yscrollcommand=scrollbar_response.set,
        )
        self.entree_question = SimpleMarkdownText(
            self.cnv_question, height=5, font=default_font
        )
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
        self.entree_question.bind("<Control-Return>", func=self.submission)
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
            self.entree_prompt.insert_markdown(content)
        except:
            (
                self.entree_prompt.insert_markdown(
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
            height=int(self.entree_response.cget("height")) + 2, width=100
        )
        self.entree_question.configure(height=5, width=100)
        self.entree_question.pack_propagate()
        self.entree_response.pack_propagate()

    def normalize_me(self):
        self.entree_response.configure(height=5, width=100)
        self.entree_question.configure(height=5, width=100)
        self.entree_question.pack_propagate()
        self.entree_response.pack_propagate()

    def minimize_me(self):
        self.entree_response.configure(
            height=int(self.entree_response.cget("height")) - 2, width=100
        )
        self.entree_question.configure(height=0, width=100)
        self.entree_response.pack_propagate()
        self.entree_question.pack_propagate()

    def set_talker(self, talker):
        self.talker = talker

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
        self.entree_response.replace("1.0", tk.END, "")

    def lire_text_from_object(self, object: tk.Text):
        texte_to_talk = object.get("1.0", tk.END)

        if texte_to_talk != "":
            try:
                texte_to_talk = object.get(tk.SEL_FIRST, tk.SEL_LAST)
            except:
                texte_to_talk = object.get("1.0", tk.END)
            finally:
                self.talker(texte_to_talk)
