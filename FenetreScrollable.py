import datetime
import tkinter as tk
import tkinter.font as tkfont

from groq import Groq

from Constants import DARK2, MAX_HISTORY, ZEFONT, LLAMA370B
from Conversation import Conversation
from outils import (
    ask_to_resume,
    lecteur_init,
    from_rgb_to_tkColors,
    lire_haute_voix,
)
from secret import GROQ_API_KEY


class FenetreScrollable(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
        self.parent=parent
        self.prompts_history = []
        self.fontdict = tkfont.Font(
            family=ZEFONT[0],
            size=ZEFONT[1],
            slant=ZEFONT[2],
            weight=ZEFONT[3],
        )
        self.canvas = tk.Canvas(
            self,
            borderwidth=0,
            background=from_rgb_to_tkColors(DARK2),
        )
        self.frame = tk.Frame(
            self.canvas,
            background=from_rgb_to_tkColors(DARK2),
        )
        self.vScrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vScrollbar.set)

        self.vScrollbar.pack(side="left", fill="y")
        self.frame.pack(fill="both", expand=True)
        self.canvas.create_window(
            (4, 4), window=self.frame, anchor="center", tags="self.frame"
        )
        self.canvas.pack(fill="both", expand=True)

        self.frame.bind("<Configure>", self.onFrameConfigure)
        self.responses = []
        # self.pack(fill="both", expand=True)

    def say_txt(self, text: str):
        """
        lit le texte sans passer par un thread
        """

        texte_reformate = (
            text.replace("*", " ")
            .replace("-", " ")
            .replace("=", " ")
            .replace("#", " ")
            .replace("|", " ")
            .replace("/", " ")
            .replace(":", " ")
            .replace("https", " ")
        )
        lecteur_init().say(texte_reformate)
        lecteur_init().runAndWait()
        lecteur_init().stop()

    def get_prompts_history(self) -> list:
        return self.prompts_history

    def supprimer_conversation(self, evt: tk.Event):
        widgt: Conversation = evt.widget
        print("Effacement de la conversation ::" + widgt.winfo_name() + "::")
        widgt.supprimer_conversation()
        for mini_dict in self.get_prompts_history():
            if widgt.winfo_name() in mini_dict["fenetre_name"]:
                self.get_prompts_history().remove(mini_dict)
                break
        self.responses.remove(widgt)


    def addthing(
        self,
        _timing,
        agent_appel,
        simple_text: str,
        ai_response: str,
        model,
        submit_func,
    ):
        self.model = model
        fenetre_response: Conversation = Conversation(
            ai_response=ai_response,
            text=simple_text,
            master=self.frame,
            submit=submit_func,
            agent_appel=agent_appel,
            model_to_use=model,
        )
        fenetre_response.pack(fill="both",expand=True)

        self.responses.append(fenetre_response)

        self.save_to_history(fenetre_response.winfo_name(), simple_text, ai_response)
        fenetre_response.bind(
            "<Destroy>",
            func=self.supprimer_conversation,
        )

        fenetre_response.get_entree_response().insert_markdown(
            "_" + datetime.datetime.now().isoformat() + " <" + self.model + ">_ - ",
        )
        fenetre_response.get_entree_response().insert_markdown(
            "_" + str(_timing) + "secondes < " + str(type(agent_appel)) + " >_\n",
        )
        fenetre_response.get_entree_response().insert_markdown(ai_response + "\n")

        fenetre_response.get_entree_question().insert_markdown(
            datetime.datetime.now().isoformat() + " <" + self.model + "> :: ",
        )
        fenetre_response.get_entree_question().insert_markdown(
            str(_timing) + "secondes < " + str(type(agent_appel)) + " >\n",
        )

        fenetre_response.get_entree_question().insert_markdown(simple_text + "\n")

    def print_liste_des_conversations(self):
        print("liste des conversations\n************************************")
        for item in self.get_prompts_history():
            print(
                item["fenetre_name"]
                + ":: \n-----------------------"
                + "\nPrompt:: "
                + str(
                    item["prompt"][:60] + "... "
                    if len(item["prompt"]) >= 59
                    else item["prompt"]
                )
                + "Response:: "
                + str(
                    item["response"][:59] + "...\n"
                    if len(item["response"]) >= 60
                    else item["response"] + "\n"
                )
            )
        print("************************************")

    def save_to_history(self, fenetre_name, question, ai_response):
        """
        #### crée une sauvegarde des anciens échanges:
        Lorsque les conversations sont effacées de la fenêtre scrollable,
        la conversation correspondande est effacée aussi de la liste.
        cela permet de gerer la continuite de la conversation avec
        une certaie profondeur (à la discrétions de l'utilisateur) tout
        en évitant d'engorger la mémoire et les tokens utilisé
        """
        prompt = question[:499] if len(question) >= 500 else question
        response = ai_response[:499] if len(ai_response) >= 500 else ai_response
        longueur = len(self.get_prompts_history())

        # check if len(list)>MAX_HISTORY
        if longueur >= MAX_HISTORY:
            # on fait un résumé des 10 anciennes conversations (MAX_HISTORY=15)
            conversation_resumee = ask_to_resume(
                agent_appel=Groq(api_key=GROQ_API_KEY),
                prompt="".join(map(str, self.get_prompts_history())),
                model_to_use=LLAMA370B,
            )

            # on les efface
            self.get_prompts_history().clear()

            # on insère le résumé des conversations
            self.get_prompts_history().append(
                {
                    "fenetre_name": fenetre_name,
                    "prompt": "Résumé des conversations précédente",
                    "response": conversation_resumee,
                },
            )
            lire_haute_voix("un résumé des anciennes conversations à été effectué")

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
