import tkinter as tk

from outils import from_rgb_to_tkColors
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

    entree_prompt_principal: SimpleMarkdownText
    ai_response: str

    boutton_effacer_entree_response: tk.Button
    bouton_lire_responses: tk.Button
    bouton_transfere: tk.Button
    entree_response: SimpleMarkdownText
    entree_question: SimpleMarkdownText
    talker: any

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
                self.talker(texte_to_talk, False)

    def __init__(
        self,
        master: tk.Frame,
        entree_recup: SimpleMarkdownText,
        ai_response: str,
    ):
        super().__init__(master)
        self.master = master
        self.pack()
        self.title = "title"
        self.ai_response = ai_response
        self.entree_prompt_principal = entree_recup
        canvas_edition = tk.Canvas(master=master, relief="sunken")

        boutons_cnv_response = tk.Frame(canvas_edition)
        cnv_globals_responses = tk.Frame(canvas_edition)
        cnv_response = tk.Frame(cnv_globals_responses, relief="sunken")
        cnv_question = tk.Frame(cnv_globals_responses, relief="sunken")

        # TODO : transformer les entree_prompt_principal et entree_response en liste
        # de plusieurs question_tk_text et reponse_tk_text

        boutton_supprimer_question_response = tk.Button(
            boutons_cnv_response, text=" X ", command=self.destroy
        )

        boutton_supprimer_question_response.configure(
            bg=from_rgb_to_tkColors(DARK2), fg=from_rgb_to_tkColors(LIGHT3)
        )
        boutton_supprimer_question_response.pack(side="right")

        boutton_effacer_entree_response = tk.Button(
            boutons_cnv_response, text="Effacer", command=self.clear_entree_response
        )

        boutton_effacer_entree_response.configure(
            bg=from_rgb_to_tkColors(DARK2), fg=from_rgb_to_tkColors(LIGHT3)
        )
        boutton_effacer_entree_response.pack(side="right")

        bouton_lire_responses = tk.Button(
            boutons_cnv_response,
            text="Lire",
            command=lambda: self.lire_text_from_object(entree_response),
        )
        bouton_lire_responses.configure(
            bg=from_rgb_to_tkColors(DARK3), fg=from_rgb_to_tkColors(LIGHT3)
        )
        bouton_lire_responses.pack(side=tk.RIGHT)

        canvas_edition.pack(fill="x", expand=True)
        boutons_cnv_response.pack(fill="x", expand=True)

        cnv_globals_responses.pack(fill="x", expand=True)
        cnv_response.pack(fill="x", expand=True)
        cnv_question.pack(fill="x", expand=True)

        bouton_transfere = tk.Button(
            boutons_cnv_response,
            text="Transférer",
            command=lambda: self.entree_prompt_principal.insert_markdown(
                self.get_ai_response()
            ),
            bg=from_rgb_to_tkColors(LIGHT1),
            fg=from_rgb_to_tkColors(DARK3),
        )
        bouton_transfere.pack(side=tk.RIGHT, fill="both")
        scrollbar_response = tk.Scrollbar(cnv_response)
        scrollbar_response.pack(side=tk.RIGHT, fill="both")
        scrollbar_question = tk.Scrollbar(cnv_question)
        scrollbar_question.pack(side=tk.RIGHT, fill="both")
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=8)
        entree_response = SimpleMarkdownText(cnv_response, font=default_font)
        entree_response.configure(
            bg=from_rgb_to_tkColors(LIGHT3),
            fg=from_rgb_to_tkColors(DARK1),
            height=5,
            font=("Arial", 12),
            wrap="word",
            padx=10,
            pady=6,
            yscrollcommand=scrollbar_response.set,
        )
        entree_question = SimpleMarkdownText(cnv_question, height=5, font=default_font)
        entree_question.configure(
            bg=from_rgb_to_tkColors(LIGHT2),
            fg=from_rgb_to_tkColors(DARK3),
            height=4,
            wrap="word",
            padx=10,
            pady=6,
            yscrollcommand=scrollbar_question.set,
        )
        entree_response.pack(fill="both", expand=True)
        entree_question.pack(fill="both", expand=True)

        scrollbar_response.configure(
            command=entree_response.yview, bg=from_rgb_to_tkColors(DARK2)
        )
        scrollbar_question.configure(
            command=entree_question.yview, bg=from_rgb_to_tkColors(DARK2)
        )

        self.entree_response = entree_response
        self.entree_question = entree_question
