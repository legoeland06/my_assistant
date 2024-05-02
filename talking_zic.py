import tkinter as tk
import pyttsx3 as talker
from tkinter import messagebox

lecteur = talker.init()
lecteur.setProperty("lang", "french")
lecteur.setProperty("rate", "180")
talker.speak("Zic Lecteur Auto")

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
    def creer_fenetre(self, title, msg_to_write, moteur_de_diction):
        # Création de la fenêtre principale
        fenetre = tk.Tk()
        fenetre.title(self.title + " - " + title)

        # p = pyaudio.PyAudio()
        # stream = p.open(
        #     format=pyaudio.paInt16,
        #     channels=1,
        #     rate=16000,
        #     input=True,
        #     frames_per_buffer=8192,
        # )
        
        # my_engine_just_load=engine_model
        # rec = vosk.KaldiRecognizer(my_engine_just_load, 16000)

        # fenetre_dictee = tk.Tk(
        #     screenName="Dictée vocale",
        #     baseName="dictee_vocale",
        #     className="DicteeVocale",
        # )
        
        # Création d'un champ de saisie de l'utilisateur
        entree1 = tk.Text(fenetre)
        entree1.insert(tk.END, msg_to_write)

        entree1.pack(fill="both", expand=True)

        def quitter():
            # Afficher une boîte de message de confirmation
            reponse = messagebox.askyesno(
                "Confirmation", "Êtes-vous sûr de vouloir quitter ?"
            )
            if reponse:
                self.set_submission(entree1.get("1.0", "end"))
                fenetre.destroy()
            else:
                print("L'utilisateur a annulé.")

        def lire_texte():
            dude=entree1.get("1.0", "end")
            moteur_de_diction.speak(dude)

        bouton_lire = tk.Button(fenetre, text="Lire", command=lire_texte)
        bouton_lire.pack()

        # Création d'un bouton pour quitter
        bouton_quitter = tk.Button(fenetre, text="Quitter", command=quitter)
        bouton_quitter.pack()

        # Affichage de la fenêtre
        fenetre.mainloop()


        def lire_contenu():

            try:
                kiki=entree_dictee.selection_get()
                moteur_de_diction(kiki,stop_ecoute=False)
            except: 
                moteur_de_diction(entree_dictee.get("1.0",tk.END),stop_ecoute=False)
            

        def lance_ecoute()->str:
            my_timer=0

            entree_dictee.update()
            while True:
                reco_text=""
                data = stream.read(
                    num_frames=4096, exception_on_overflow=False
                )  # read in chunks of 4096 bytes

                if rec.AcceptWaveform(data):  # accept waveform of input voice
                    # Parse the JSON result and get the recognized text
                    result = json.loads(rec.Result())
                    reco_text = result["text"]

                    if "terminer l'enregistrement" in reco_text.lower():
                        moteur_de_diction("Pause de l'enregistrement. Vous pouvez le reprendre en appuyant sur démarrer la diction.",stop_ecoute=True)
                        break

                    elif reco_text!="":
                        entree_dictee.insert(tk.END, reco_text+"\n")

                    entree_dictee.update()

            entree_dictee = tk.Text(fenetre_dictee)
            entree_dictee.pack(fill="y", expand=True)

            bouton_commencer_diction=tk.Button(fenetre_dictee,text="commencer la diction",command=lance_ecoute)
            bouton_commencer_diction.pack(fill="y", expand=True)

            bouton_lire_contenu=tk.Button(fenetre_dictee,text="lire",command=lire_contenu)
            bouton_lire_contenu.pack(fill="y", expand=True)

            fenetre_dictee.mainloop()


def lire_haute_voix(texte_a_lire, talker):
    fenetre_de_lecture = fenetre_entree()
    fenetre_de_lecture.creer_fenetre(
        "TalkingZicBot", msg_to_write=texte_a_lire, moteur_de_diction=talker
    )


def main(alire: str):
    lire_haute_voix(texte_a_lire=alire, talker=talker)


if __name__ == "__main__":
    main(alire="Coller ici votre texte à me faire lire")
