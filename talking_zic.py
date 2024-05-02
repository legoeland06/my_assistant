import tkinter as tk
import pyttsx3 as talker
from tkinter import messagebox


class fenetre_entree:
    content: str
    title: str
    submission: str

    def __init__(self):
        self.title = "ZicChatBot"
        self.content = ""
        self.submission = ""

    def set(self, content: str):
        self.content = content

    def get(self) -> str:
        return self.content

    def set_submission(self, content: str):
        self.submission = content

    def get_submission(self) -> str:
        return self.submission

    # open a windows
    def creer_fenetre(self, title, msg_to_write):

        fenetre = tk.Tk()
        fenetre.title(self.title + " - " + title)

        # Création d'un champ de saisie de l'utilisateur
        enter1 = tk.Text(fenetre)
        enter1.insert(tk.END, msg_to_write)

        enter1.pack(fill="both", expand=True)

        def quitter():
            # Afficher une boîte de message de confirmation
            reponse = messagebox.askyesno(
                "Confirmation", "Êtes-vous sûr de vouloir quitter ?"
            )
            if reponse:
                self.set_submission(enter1.get("1.0", "end"))
                fenetre.destroy()
            else:
                print("L'utilisateur a annulé.")

        def lire_texte():
            try:
                dire(enter1.selection_get())
            except:
                dire(enter1.get("1.0", tk.END))

        bouton_lire = tk.Button(fenetre, text="Lire", command=lire_texte)
        bouton_lire.pack()

        # Création d'un bouton pour quitter
        bouton_quitter = tk.Button(fenetre, text="Quitter", command=quitter)
        bouton_quitter.pack()

        # Affichage de la fenêtre
        fenetre.mainloop()


def create_instance_lecteur():
    lecteur = talker
    lecteur_init = lecteur.init()
    lecteur_init.setProperty("lang", "french")
    lecteur_init.setProperty("rate", "180")
    lecteur.speak("Zic Lecteur Auto")
    return lecteur


def ouvrir_app(texte_initial: str):
    fenetre_de_lecture = fenetre_entree()
    print(fenetre_de_lecture.creer_fenetre("TalkingZicBot", msg_to_write=texte_initial))


def dire(texte_a_lire: str):
    lecteur.speak(text=texte_a_lire)


def main(alire: str):
    ouvrir_app(texte_initial=alire)


lecteur = create_instance_lecteur()

if __name__ == "__main__":
    main(alire="Coller ici votre texte à me faire lire")
