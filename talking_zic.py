import tkinter as tk
import pyttsx3 as talker
from tkinter import messagebox
from PIL import Image, ImageTk


class fenetre_entree:
    content: str
    title: str
    submission: str

    def __init__(self):
        self.title = "ZicChatBot"
        self.content = ""
        self.submission = ""
        self.creer_fenetre(
            "TalkingZicBot",
            msg_to_write="Veuillez écrire ou coller ici le texte à me faire lire...",
        )

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
        """appelle la fenetre de diction"""

        fenetre = tk.Tk()
        fenetre.title(self.title + " - " + title)

        def quitter():
            """quitte la fenetre et set son attribut submission pour récupération ultérieure"""
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
            """par défault, lit la sélection, sinon lit tout le texte à haute voix"""
            try:
                texte = enter1.selection_get()
            except:
                texte = enter1.get("1.0", tk.END)
            finally:
                dire(texte)

        def affiche_illustration(image, fenetre, message):
            # ## PRESENTATION DU GOELAND  ####
            cnvs1 = tk.Frame(fenetre)
            cnvs1.configure(bg=_from_rgb((69, 122, 188)))
            cnvs1.pack(fill="x", expand=False)
            # ################################
            cnvs2 = tk.Frame(cnvs1)
            cnvs2.configure(bg="grey")
            cnvs2.pack(fill="x", expand=False)

            bouton_lire = tk.Button(cnvs2, text="Lire", command=lire_texte)

            bouton_lire.configure(bg="black", fg="white")
            bouton_lire.pack(side=tk.LEFT)
            # Create a canvas
            canva = tk.Canvas(cnvs1, height=100, bg=_from_rgb((69, 122, 188)))

            label = tk.Label(
                cnvs2,
                text=message,
                font=("Trebuchet", 8),
                fg="white",
                bg="grey",
            )
            label.pack(side=tk.RIGHT, expand=False)

            # Add the image to the canvas, anchored at the top-left (northwest) corner
            canva.create_image(0, 0, anchor="nw", image=image, tags="bg_img")
            canva.pack(fill="x", expand=True)

        my_image = ImageTk.PhotoImage(Image.open("IMG_20230619_090300.jpg"))
        affiche_illustration(my_image, fenetre, "... Jonathan Livingston dit legoeland")

        # Création d'un champ de saisie de l'utilisateur
        enter1 = tk.Text(fenetre)
        enter1.configure(bg="grey", fg="white")
        enter1.insert(tk.END, msg_to_write)

        enter1.pack(fill="both", expand=True)

        # Création d'un bouton pour quitter
        bouton_quitter = tk.Button(fenetre, text="Quitter", command=quitter)
        bouton_quitter.pack()

        # Affichage de la fenêtre
        fenetre.mainloop()


def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code"""
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


def create_instance_lecteur():
    lecteur = talker
    lecteur_init = lecteur.init()
    lecteur_init.setProperty("lang", "french")
    lecteur_init.setProperty("rate", "180")
    lecteur.speak("Zic Lecteur Auto")
    return lecteur


def ouvrir_app(texte_initial: str):
    # appel de l'application
    fenetre_de_lecture = fenetre_entree()
    print(
        "\n"
        + "=" * 100
        + "\nDernier texte lu:\n"
        + "=" * 100
        + "\n[\n"
        + fenetre_de_lecture.get_submission()
        + "\n\t]\n"
        + "=" * 100
        + "\n"
    )


def dire(texte_a_lire: str):
    """lit à haute voix le contenu de texte_a_lire, sinon dit qu'il n'y a rien à lire"""
    if not texte_a_lire.isspace():
        lecteur.speak(text=texte_a_lire)
    else:
        lecteur.speak(text="rien à lire")


def main(alire: str):
    ouvrir_app(texte_initial=alire)


lecteur = create_instance_lecteur()

if __name__ == "__main__":
    main(alire="Coller ici votre texte à me faire lire")
