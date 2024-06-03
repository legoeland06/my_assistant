import datetime
import tkinter as tk

from FenetreResponse import FenetreResponse
from SimpleMarkdownText import SimpleMarkdownText
from outils import from_rgb_to_tkColors


class FenetreScrollable(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.configure(height=600,width=800)
        self.canvas = tk.Canvas(self, borderwidth=0,background="#ffffff",height=600,)
        self.frame = tk.Frame(self.canvas, background="#ffffff", height=600,width=700)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack( fill="both", expand=False)
        self.canvas.create_window(
            (4, 4), window=self.frame, anchor="nw", tags="self.frame"
        )

        self.frame.bind("<Configure>", self.onFrameConfigure)
        self.responses = []

        # self.populate()

    def addthing(
        self,
        _timing,
        agent_appel,
        simple_markdown: SimpleMarkdownText,
        ai_response,
        talker,
        model,
    ):
        self.model=model
        fenetre_response = FenetreResponse(
            ai_response=ai_response,
            entree_recup=simple_markdown,
            master=self.frame,
        )
        self.responses.append(fenetre_response)
        fenetre_response.set_talker(talker=talker)
        fenetre_response.get_entree_response().tag_configure(
            tagName="boldtext",
            font=(
                fenetre_response.get_entree_response().cget("font") + " italic",
                8,
            ),
        )
        #
        fenetre_response.get_entree_response().tag_configure(
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
        fenetre_response.get_entree_response().tag_configure(
            "balise",
            font=(
                fenetre_response.get_entree_response(),
                8,
            ),
            foreground=from_rgb_to_tkColors((100, 100, 100)),
        )

        fenetre_response.get_entree_response().tag_configure(
            "balise_bold",
            font=(fenetre_response.get_entree_response().cget("font") + " bold", 8),
            foreground=from_rgb_to_tkColors((100, 100, 100)),
        )
        fenetre_response.get_entree_response().insert(
            tk.END,
            datetime.datetime.now().isoformat() + " <" + self.model + "> - ",
            "balise",
        )
        fenetre_response.get_entree_response().insert(
            tk.END,
            str(_timing) + "secondes < " + str(type(agent_appel)) + " >\n",
            "balise_bold",
        )
        # fenetre_response.get_entree_response().insert(tk.END, readable_ai_response, "response")
        fenetre_response.get_entree_response().insert_markdown(ai_response + "\n\n")
        # fenetre_response.get_entree_response().insert(tk.END, "\n\n" + "</" + self.get_model() + ">\n\n", "balise")

        fenetre_response.get_entree_question().configure(font=("Arial", 10))
        fenetre_response.get_entree_question().tag_configure(
            tagName="boldtext",
            font=(
                fenetre_response.get_entree_response().cget("font") + " italic",
                8,
            ),
        )
        fenetre_response.get_entree_question().tag_configure(
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
        fenetre_response.get_entree_question().tag_configure(
            "balise",
            font=(
                fenetre_response.get_entree_question().cget("font") + " italic",
                8,
            ),
            foreground=from_rgb_to_tkColors((100, 100, 100)),
        )
        fenetre_response.get_entree_question().tag_configure(
            "balise_bold",
            font=(fenetre_response.get_entree_question().cget("font") + " bold", 8),
            foreground=from_rgb_to_tkColors((100, 100, 100)),
        )
        fenetre_response.get_entree_question().insert(
            tk.END,
            datetime.datetime.now().isoformat() + " <" + self.model + "> :: ",
            "balise",
        )
        fenetre_response.get_entree_question().insert(
            tk.END,
            str(_timing) + "secondes < " + str(type(agent_appel)) + " >\n",
            "balise_bold",
        )

        # fenetre_response.set_entree_question(simple_markdown)
        fenetre_response.get_entree_question().insert_markdown(
            simple_markdown.get("1.0", tk.END) + "\n"
        )
        fenetre_response.get_entree_response().update()
        fenetre_response.get_entree_question().update()

    def onFrameConfigure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
