import datetime
import tkinter as tk

from Constants import DARK2
from FenetreResponse import FenetreResponse
from SimpleMarkdownText import SimpleMarkdownText
from outils import from_rgb_to_tkColors


class FenetreScrollable(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        self.prompts_history=[]
        tk.Frame.__init__(self, parent)
        self.canvas = tk.Canvas(
            self,
            borderwidth=0,
            height=int(parent.winfo_reqheight()) + 400,
            width=self.master.winfo_reqwidth() - 20,
            background=from_rgb_to_tkColors(DARK2),
        )
        self.frame = tk.Frame(
            self.canvas,
            height=int(parent.winfo_reqheight()) + 400,
            width=self.master.winfo_reqwidth() - 20,
            background=from_rgb_to_tkColors(DARK2),
        )
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=False)
        self.canvas.create_window(
            (4, 4), window=self.frame, anchor="center", tags="self.frame"
        )

        self.frame.bind("<Configure>", self.onFrameConfigure)
        self.responses = []

    def get_prompts_history(self) -> list:
        return self.prompts_history

    def supprimer_conversation(self, evt: tk.Event):
        widgt: tk.Widget = evt.widget
        print("Effacement de la conversation ::" + widgt.winfo_name() + "::")
        for mini_dict in self.get_prompts_history():
            if widgt.winfo_name() in mini_dict["fenetre_name"]:
                self.get_prompts_history().remove(mini_dict)
                break

    def addthing(
        self,
        _timing,
        agent_appel,
        simple_markdown_text: SimpleMarkdownText,
        ai_response: str,
        talker,
        model,
        submit_func,
    ):
        self.model = model
        fenetre_response = FenetreResponse(
            ai_response=ai_response,
            entree_recup=simple_markdown_text,
            master=self.frame,
            submit=submit_func,
            agent_appel=agent_appel,
            model_to_use=model,
        )
        self.responses.append(fenetre_response)

        self.save_to_history(
            fenetre_response.winfo_name(), simple_markdown_text.get_text(), ai_response
        )
        fenetre_response.bind(
            "<Destroy>",
            func=self.supprimer_conversation,
        )
        fenetre_response.set_talker(talker=talker)
        fenetre_response.get_entree_response().configure(font=("Arial", 10))
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
        fenetre_response.get_entree_response().insert_markdown(ai_response + "\n\n")

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

        fenetre_response.get_entree_question().insert_markdown(
            simple_markdown_text.get_text() + "\n"
        )
        fenetre_response.get_entree_response().update()
        fenetre_response.get_entree_question().update()

        self.print_liste_des_conversations()

    def print_liste_des_conversations(self):
        print("liste des conversations\n************************************")
        for item in self.get_prompts_history():
            print(
                item["fenetre_name"]
                + ":: \n-----------------------"
                + "\nPrompt:: "+ str(
                    item["prompt"][:60] + "... "
                    if len(item["prompt"]) >= 59
                    else item["prompt"]
                )
                + "Response:: " + str(item["response"][:59]
                + "...\n"
                if len(item["response"]) >= 60
                else item["response"]+"\n")
            )
        print("************************************")

    def save_to_history(self, fenetre_name, question, ai_response):
        """
        ## crée une sauvegarde des anciens échanges:
        Lorsque les conversations sont effacées de la fenêtre scrollable,
        la conversation correspondande est effacée aussi de la liste.
        cela permet de gerer la continuite de la conversation avec
        une certaie profondeur (à la discrétions de l'utilisateur) tout
        en évitant d'engorger la mémoire et les tokens utilisé
        """
        prompt = question[:499] if len(question) >= 500 else question
        response = ai_response[:499] if len(ai_response) >= 500 else ai_response
        self.get_prompts_history().append(
            {
                "fenetre_name": fenetre_name,
                "prompt": prompt,
                "response": response,
            },
        )

    def onFrameConfigure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
