from datetime import datetime

import json
import random
import sys
import time
from tkinter import filedialog, messagebox, simpledialog
from typing import Any, Tuple
from groq import Groq
import ollama
from openai import ChatCompletion  # type: ignore
import pyaudio
from Article import Article
from Constants import *
import tkinter.font as tkfont
import tkinter as tk
import vosk
from PIL import Image, ImageTk
import threading

from Conversation import Conversation
from FenetreScrollable import FenetreScrollable
from GrandeFenetre import GrandeFenetre
from RechercheArticles import RechercheArticles
from SimpleMarkdownText import SimpleMarkdownText
from StoppableThread import StoppableThread
import my_feedparser_rss
from secret import GROQ_API_KEY

from outils import (
    _traitement_du_texte,
    getStream,
    threads_outils,
    append_saved_texte,
    ask_to_ai,
    ask_to_resume,
    chargeImage,
    downloadimage,
    getNewsApi,
    create_asyncio_task,
    lancer_chrome,
    lancer_search_chrome,
    lecteur_init,
    from_rgb_to_tkColors,
    get_groq_ia_list,
    get_pre_prompt,
    getEngine,
    letters_to_number,
    lire_haute_voix,
    load_pdf,
    load_txt,
    make_resume,
    questionOuiouNon,
    questionOuverte,
    read_text_file,
    tester_appelation,
    traitement_du_texte,
    translate_it,
)

type History = list[Conversation]


class FenetrePrincipale(tk.Frame):
    streaming: pyaudio.Stream
    engine_model: vosk.KaldiRecognizer

    def __init__(
        self,
        title: str,
        # model ia à utiliser
        model_to_use: str,
        master,
    ):
        super().__init__(master)
        self.master = master
        self.ia = LLAMA3
        self.debride = False
        self.history = []
        self.searchHystory = []
        self.title = title
        self.ai_response = str()
        self.nb_mots = 4
        self.threads = []
        self.valide = True
        self.ok_to_Read = True
        self.prompts_history = []
        self.responses = []
        self.submission = str()
        self.mode_prompt = False
        self.fontdict = tkfont.Font(
            family=ZEFONT[0],
            size=ZEFONT[1],
            slant=ZEFONT[2],
            weight=ZEFONT[3],
        )
        # self.engine_model: vosk.KaldiRecognizer
        self.default_font = tkfont.nametofont("TkDefaultFont")
        self.default_font.configure(size=14)
        self.btn_font = tkfont.nametofont("TkIconFont")
        self.btn_font.configure(size=14)
        self.timer: float = 0
        self.model_to_use = model_to_use
        self.image: ImageTk.PhotoImage = ImageTk.PhotoImage(
            Image.open("banniere.png").reduce(2)
        )  # type: ignore
        self.image_button_diction1 = chargeImage("oeil1.jpg", 200)
        self.image_button_diction2 = chargeImage("oeil2.jpg", 200)
        self.image_button_diction3 = chargeImage("oeil3.jpg", 200)

        self.image_link = str()
        self.content = str()
        self.widgetMotcles: tk.Entry | None = None

        # phase de construction de la fenetre principale
        self.creer_fenetre(
            image=self.get_image(),
            msg_to_write="Prompt...",
        )
        # self.toplel=tk.Toplevel()
        self.my_liste = []
        self.messages = [
            {
                "role": "user",
                "content": "Bonjour",
            },
        ]
        self.actual_chat_completion = []
        self.engine_model = getEngine()
        self.streaming = getStream()
        # Mode de développement
        # BYPASS les sélection IHM chronophages en mode dev
        self.bypass()
        # après cette invocation l'application est lancée en mode audioChat directement

        self.pack(fill="both", expand=False)
        self.fenetre_scrollable = FenetreScrollable(self.master)
        self.fenetre_scrollable.pack(fill="both", expand=True)

    #####################################################################################
    # DEBUT DES GETTERS SETTERS
    #####################################################################################

    def bypass(self):
        """by pass les sélections dIa et de client"""
        groq_client = Groq(api_key=GROQ_API_KEY)
        self.set_client(groq_client)
        self.set_model(LLAMA370B)
        self.lance_thread_ecoute()

    def set_debride(self, status: bool):
        self.debride = status

    def get_debride(self) -> bool:
        return self.debride

    def set_ok_to_Read(self, ok_to_Read: bool):
        """setter for chatAudioMode"""
        self.ok_to_Read = ok_to_Read

    def get_ok_to_Read(self) -> bool:
        """getter for chatAudioMode"""
        return self.ok_to_Read

    def setValide(self, valide: bool):
        self.valide = valide

    def getValide(self) -> bool:
        return self.valide

    def getListOfModels(self):
        return [element["name"] for element in (ollama.list())["models"]]

    def get_actual_chat_completion(self) -> list:
        return self.actual_chat_completion

    def set_thread(self, thread: StoppableThread):
        self.thread = thread

    def get_thread(self) -> StoppableThread:
        return self.thread  # type: ignore

    def set_timer(self, timer: float):
        self.timer = timer

    def get_timer(self) -> float:
        return self.timer

    def set_ai_response(self, response: str):
        self.ai_response = response

    def get_ai_response(self) -> str:
        return self.ai_response

    # ici on pourra pointer sur un model hugginface plus rapide à répondre mais en ligne
    def set_client(self, client: Any):
        self.client = client
        lire_haute_voix("changement du client : " + str(type(self.client)))

    def get_client(self) -> Any:
        return self.client

    def get_motcles(self) -> list[str]:
        if (
            isinstance(self.widgetMotcles, tk.Entry)
            and self.widgetMotcles.get().__len__()
        ):
            motcles: list[str] = self.widgetMotcles.get().split()
            return motcles
        else:
            return []

    def set(self, content: str):
        self.content = content

    def get(self) -> str:
        return self.content

    def set_submission(self, content: str):
        """
        remplace tout le contenu de l'attribut **submission** de lma classe, par la valeur de **content**
        """
        self.submission = content

    def get_submission(self) -> str:
        return self.submission

    def get_image_link(self) -> str:
        return self.image_link

    def set_image_link(self, image_link: str):
        self.image_link = image_link

    def set_model(self, name_ia: str) -> bool:
        self.model_to_use = name_ia
        return (
            True if lire_haute_voix("changement d'ia: " + self.model_to_use) else False
        )

    def get_model(self) -> str:
        return self.model_to_use

    def set_stream(self, stream: pyaudio.Stream) -> bool:
        self.streaming = stream
        return True

    def get_stream(self) -> pyaudio.Stream:
        # return getStream()
        return self.streaming

    def get_engine(self) -> vosk.KaldiRecognizer:
        return self.engine_model

    def get_image(self) -> ImageTk.PhotoImage:  # type: ignore
        return self.image

    def set_image(self, image: ImageTk.PhotoImage) -> bool:  # type: ignore
        self.image = image
        return True

    #####################################################################################
    # FIN DES GETTERS SETTERS
    #####################################################################################

    # open a windows
    def affiche_banniere(self, image_banniere: ImageTk.PhotoImage, slogan):  # type: ignore
        """affiche l'illustration (la bannière) et les boutons de saisie système
        * bouton quitter
        * sélection du clien Ola ou ollama...
        * sélection du modèle d'ia ...."""
        # ## PRESENTATION DU GOELAND  ####
        self.canvas_principal_banniere = tk.Frame(
            self, background=from_rgb_to_tkColors(DARK2), name="cnvs1"
        )
        # self.canvas_principal_banniere.configure(height=BANNIERE_HEIGHT/2)
        self.canvas_principal_banniere.pack(fill="x", expand=True)
        # ################################
        self.canvas_buttons_banniere = tk.Frame(
            self.canvas_principal_banniere, name="cnvs2"
        )
        self.canvas_buttons_banniere.configure(bg=from_rgb_to_tkColors(DARK3))
        self.canvas_buttons_banniere.pack(fill="x", expand=False)

        # Create a canvas
        self.canvas_image_banniere = tk.Canvas(
            self.canvas_principal_banniere,
            height=BANNIERE_HEIGHT,
            # width=BANNIERE_WIDTH,
            background=from_rgb_to_tkColors(DARK2),
            name="canva",
        )

        # Création d'un bouton pour quitter
        self.bouton_quitter = tk.Button(
            self.canvas_buttons_banniere,
            font=self.btn_font,
            relief="flat",
            text="📴",
            border=0,
            command=self.quitter,
        )
        self.bouton_quitter.configure(background="black", foreground="red")
        self.bouton_quitter.pack(side=tk.LEFT)

        self.bouton_Groq = tk.Button(
            self.canvas_buttons_banniere,
            font=self.btn_font,
            text="🚹",
            command=self.groq_choix_ia,
            relief="flat",
            highlightthickness=3,
            highlightcolor="yellow",
        )
        self.bouton_Groq.configure(foreground="red", background="black")
        self.bouton_Groq.pack(side=tk.LEFT)

        self.info_web_status = tk.Button(
            self.canvas_buttons_banniere,
            font=self.btn_font,
            text="🔘",
            command=self.groq_choix_ia,
            relief="flat",
            highlightthickness=3,
            highlightcolor="yellow",
        )
        self.info_web_status.configure(foreground="grey", background="black")
        self.info_web_status.pack(side=tk.LEFT)

        self.bouton_LargePolice = tk.Button(
            self.canvas_buttons_banniere,
            font=self.btn_font,
            text="+",
            command=self.enlarge,
            relief="flat",
            highlightthickness=3,
            highlightcolor="yellow",
        )
        self.bouton_LargePolice.configure(foreground="red", background="black")
        self.bouton_LargePolice.pack(side=tk.LEFT)

        self.bouton_DiminuePolice = tk.Button(
            self.canvas_buttons_banniere,
            font=self.btn_font,
            text="-",
            command=self.diminue,
            relief="flat",
            highlightthickness=3,
            highlightcolor="yellow",
        )
        self.bouton_DiminuePolice.configure(foreground="red", background="black")

        self.bouton_informations = tk.Button(
            self.canvas_buttons_banniere,
            font=self.btn_font,
            text="NEWS",
            command=self.recup_inf,
            relief="flat",
            highlightthickness=3,
            highlightcolor="yellow",
            activeforeground="white",
        )
        self.bouton_informations.configure(foreground="red", background="black")

        # await self.recup_informations()
        self.bouton_informations.pack(side=tk.LEFT)

        self.bouton_active_debride = tk.Button(
            self.canvas_buttons_banniere,
            font=self.btn_font,
            text="☢ activate",
            command=lambda: self.debride_switch(True),
            relief="flat",
            highlightthickness=3,
            highlightcolor="yellow",
            activeforeground="white",
        )
        self.bouton_active_debride.configure(foreground="red", background="black")

        # await self.recup_debriderbouton_active_debride()

        self.bouton_desactive_debride = tk.Button(
            self.canvas_buttons_banniere,
            font=self.btn_font,
            text="☢ activated",
            command=lambda: self.debride_switch(False),
            relief="flat",
            highlightthickness=3,
            highlightcolor="yellow",
            activeforeground="white",
        )
        self.bouton_desactive_debride.configure(foreground="yellow", background="black")

        # await self.recup_debriderbouton_active_debride()
        self.bouton_active_debride.pack(side=tk.LEFT)

        self.label_slogan = tk.Label(
            self.canvas_buttons_banniere,
            text=slogan,
            font=("Trebuchet Bold Italic", 8),
            bg="black",
            border=0,
            relief="flat",
            fg=from_rgb_to_tkColors(LIGHT3),
        )

        self.label_slogan.pack(side=tk.RIGHT, expand=False)

        # Add the image to the canvas, anchored at the top-left (northwest) corner
        self.canvas_image_banniere.create_image(
            0, 0, anchor="nw", image=image_banniere, tags="bg_img"
        )
        self.canvas_image_banniere.pack(fill="x", expand=True)

    def save_to_submission(self) -> bool:
        # si une sélection est faite dans le prompt principale,
        # elle est enregistrée dans la variable <selection>
        # sinon c'est tout le contenu du prompt qui est enregistré
        try:
            selection = self.entree_prompt_principal.get(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            selection = self.entree_prompt_principal.get("1.0", tk.END)
        finally:
            # copie le contenu de la variable <selection>
            # dans la variable submission de la classe
            # et renvoi True
            # si selection n'est pas vide

            if len(selection) > 1:
                self.set_submission(
                    content=selection + "\n",
                )
                return True
            # renvois aussi True si il y avait toujourss quelque chose dans la variable submission
            elif len(self.get_submission().lower()) > 1:
                return True
            # sinon renvoi False
            else:
                return False

    def debride_switch(self, status):
        self.set_debride(status=status)
        if self.get_debride():
            self.bouton_desactive_debride.pack(side=tk.LEFT)
            self.bouton_active_debride.pack_forget()
        else:
            self.bouton_active_debride.pack(side=tk.LEFT)
            self.bouton_desactive_debride.pack_forget()

        # self.update()

    def quitter(self):
        # Afficher une boîte de message de confirmation
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir quitter ?"):
            self.save_to_submission()
            mainthread = threading.main_thread()
            for i in threading.enumerate():
                # e:StoppableThread=(StoppableThread) i # type: ignore
                if i != mainthread:
                    print(f"ThreadThreading::{i.getName()}")
                    i.stop()  # type: ignore

            for j in self.threads:
                # e:StoppableThread=(StoppableThread)j # type: ignore
                # if isinstance(j, StoppableThread):
                j:StoppableThread=j
                print(f"ThreadThreads::{j.getName()}")
                # j.join()
                j.stop()

            for t in threads_outils:
                t:StoppableThread|threading.Thread=t
                print(f"ThreadThreading::{t.getName()}")
                if isinstance(t,StoppableThread):
                    t.stop()
                elif isinstance(t,threading.Thread):
                    t.daemon=False

            self.master.destroy()
            # mainthread.is_alive()
            # mainthread.join()
            sys.exit()

            # exit()
        else:
            print("L'utilisateur a annulé.")

    def enlarge(self):
        self.btn_font.configure(size=(self.btn_font.cget("size") + 2))
        self.fontdict.configure(size=(self.btn_font.cget("size") + 2))
        self.default_font.configure(size=(self.btn_font.cget("size") + 2))

    def diminue(self):
        self.btn_font.configure(size=(self.btn_font.cget("size") - 2))
        self.fontdict.configure(size=(self.btn_font.cget("size") - 2))
        self.default_font.configure(size=(self.btn_font.cget("size") - 2))

    def groq_choix_ia(self):
        groq_client = Groq(api_key=GROQ_API_KEY)
        self.set_client(groq_client)
        models = get_groq_ia_list(api_key=GROQ_API_KEY)
        self.affiche_ia_list(models)

    def soumettre(self) -> str:
        if self.save_to_submission():
            this_thread = StoppableThread(
                target=lambda: create_asyncio_task(async_function=self.asking())
            )
            this_thread.name = "submission"
            threads_outils.append(this_thread)
            lire_haute_voix("un instant s'il vous plait")
            list_of_words = self.get_submission().split()
            nbreCaracteres = len(self.get_submission())
            print("nombre de charactères:: " + str(nbreCaracteres))
            # TODO
            if nbreCaracteres >= 3000:
                new_prompt_list = _traitement_du_texte(self.get_submission(), 200)
                lire_haute_voix(
                    "le prompt est trop long, il est supérieur à 3000 tokens, il sera découpé en "
                    + str(len(new_prompt_list))
                    + " blocs"
                )
                for number, bloc in enumerate(new_prompt_list):
                    print(str(number) + "\n" + " ".join(bloc))
                    self.set_submission(" ".join(bloc))
                    _this = StoppableThread(
                        target=lambda: create_asyncio_task(async_function=self.asking())
                    )
                    _this.name = "part_of_submission"
                    _this.start()
                    threads_outils.append(_this)

                    time.sleep(2)
            else:
                this_thread.start()

        else:
            messagebox.showinfo(
                message=self.get_synonymsOf("Veuillez poser au moins une question")
            )

        return "Ok c'est soummis"

    def lance_thread_ecoute(self):
        self.bouton_commencer_diction.flash()
        self.bouton_commencer_diction.configure(
            image=self.image_button_diction2,  # type: ignore
            bg=from_rgb_to_tkColors((182, 78, 20)),
        )
        self.bouton_commencer_diction.update()

        # TODO: a simplifier
        self.set_thread(
            StoppableThread(
                None,
                name="mode_veille",
                target=lambda: create_asyncio_task(async_function=self.dialog_ia()),
            )
        )
        self.get_thread().daemon = True
        self.get_thread().start()
        threads_outils.append(self.get_thread())

        print("Infos Threads:\n***************************************")
        for element in self.get_thread().__dict__:
            print(element + "::" + str(self.get_thread().__dict__[element]))

    def get_synonymsOf(self, expression):
        prompt = (
            "en français exclusivement et sous la forme d'une liste non numérotée, donne 20 façons différentes de dire : ("
            + expression
            + ") dans le contexte d'un échange verbal, en réponse je ne veux rien d'autre que le résultat du type: phrase_1\nphrase_2\nphrase_3\netc...]"
        )
        _agentAppel = self.get_client()
        if isinstance(_agentAppel, Groq):
            try:
                llm: ChatCompletion = _agentAppel.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=self.get_model(),
                    temperature=1,
                    max_tokens=1024,
                    n=1,
                    stream=False,
                    stop=None,
                    timeout=10,
                )

                ai_response = llm.choices[0].message.content
            except:
                messagebox.Message("OOps, ")
                return expression
            ai_response_list = str(ai_response).split("\n")
            return ai_response_list[
                (round(random.randint(1, 19 * 10) / 10) % (len(ai_response_list) - 1))
                + 1
            ]
        return expression

    def reformule(self, expression):
        prompt = "Trouve moi une autre formulation de cette expression: " + expression
        _agentAppel = self.get_client()
        if isinstance(_agentAppel, Groq):
            try:
                llm: ChatCompletion = _agentAppel.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=self.get_model(),
                    temperature=1,
                    max_tokens=1024,
                    n=1,
                    stream=False,
                    stop=None,
                    timeout=10,
                )

                ai_response = llm.choices[0].message.content
            except:
                messagebox.Message("OOps, ")
                return expression
            ai_response_ = str(ai_response)
            return ai_response_
        return expression

    # TODO : problème ici, difficulté à arrêter le thread !!
    async def dialog_ia(self):
        content_saved_discussion = str()
        lire_haute_voix(
            "Bienvenue ! pour activer les commandes vocales, il suffit de dire : << passe en mode audio >>"
        )

        # entrez dans le mode veille
        content_saved_discussion += await self.mode_veille()

        print("Sortie de mode interactif")
        return True

    async def mode_veille(self):
        content_saved_discussion = str()
        while True:

            if self.get_stream().is_stopped():
                self.get_stream().start_stream()

            self.check_ecout: str = self.attentif()
            if self.check_ecout:
                content_saved_discussion += " " + self.check_ecout
            if "afficher de l'aide" in self.check_ecout:
                _ = self.display_help()

            elif "quel est le mode actuel" in self.check_ecout:
                self.get_stream().stop_stream()
                lire_haute_voix("nous sommes actuellement dans le mode veille")

            elif any(keyword in self.check_ecout for keyword in ["fermer", "ferme"]):
                if "l'application" in self.check_ecout:
                    self.get_stream().stop_stream()
                    self.bouton_commencer_diction.configure(
                        image=self.image_button_diction1,  # type: ignore
                        bg=from_rgb_to_tkColors(DARK0),
                    )
                    self.entree_prompt_principal.configure(
                        bg=from_rgb_to_tkColors(LIGHT0)
                    )
                    self.bouton_commencer_diction.flash()
                    self.bouton_commencer_diction.update()
                    append_saved_texte(
                        file_to_append="saved_text",
                        readable_ai_response=content_saved_discussion,
                    )
                    lire_haute_voix(
                        "ok, vous pouvez réactiver l'observeur audio en appuyant sur le bouton casque"
                    )
                    self.get_stream().close()
                    # self.get_thread().stop()

                    break

            elif any(keyword in self.check_ecout for keyword in ["active", "passe"]):
                if any(
                    keyword in self.check_ecout
                    for keyword in ["mode audio", "commande vocale"]
                ):

                    self.bouton_commencer_diction.configure(
                        image=self.image_button_diction3,  # type: ignore
                        bg=from_rgb_to_tkColors((182, 78, 20)),
                    )

                    self.entree_prompt_principal.configure(
                        bg=from_rgb_to_tkColors((DARK3)),
                        fg=from_rgb_to_tkColors((182, 78, 20)),
                    )

                    self.bouton_commencer_diction.update()
                    lire_haute_voix("pour sortir, dites : fin de la session")

                    # entrez dans le mode commandes vocale
                    content_saved_discussion += (
                        " " + await self.mode_commandes_vocales()
                    )
                elif "mode débridé" in self.check_ecout:
                    self.debride_switch(True)
                    lire_haute_voix("mode débridé activé")
                elif "mode normal" in self.check_ecout:
                    self.debride_switch(False)
                    lire_haute_voix("mode debridé désactivé")

        return content_saved_discussion

    async def mode_commandes_vocales(self):
        content_saved_discussion = str()

        _ = self.display_help()
        reserve = str()
        while True:
            self.mode_prompt = True
            self.check_ecout = self.attentif()
            if self.check_ecout:
                print("==> " + self.check_ecout)
                content_saved_discussion += " " + self.check_ecout

            if "afficher" in self.check_ecout and any(
                keyword in self.check_ecout
                for keyword in ["de l'aide", "les commandes"]
            ):
                self.mode_prompt = False
                _ = self.display_help()
                lire_haute_voix(
                    ("état des lieux de la configuration du tchat intéractif")
                )
                lire_haute_voix(
                    (
                        "je vous lis systématiquement les réponses"
                        if self.get_ok_to_Read()
                        else "les réponses ne sont pas lues"
                    )
                )
                lire_haute_voix(
                    (
                        "à la fin de votre question ou prompt valide, je vous demande si vous avez terminé"
                        if self.getValide()
                        else f"dès lors que votre prompte est valide, je déclenche ma réponse."
                    )
                )
                lire_haute_voix(
                    (
                        f"un prompt est valide dès lors qu'il contient au moins {str(self.nb_mots)} mots"
                    )
                )

            if "quel est le mode actuel" in self.check_ecout:
                self.get_stream().stop_stream()
                self.mode_prompt = False
                lire_haute_voix("nous sommes actuellement dans le mode audio")

            elif "quel jour sommes-nous" in self.check_ecout:
                self.get_stream().stop_stream()
                self.mode_prompt = False
                lire_haute_voix(
                    self.get_synonymsOf("Nous sommes le " + time.strftime("%Y-%m-%d"))
                )

            elif "quelle heure est-il" in self.check_ecout:
                self.get_stream().stop_stream()
                self.mode_prompt = False
                lire_haute_voix(
                    self.get_synonymsOf(
                        "il est exactement "
                        + time.strftime("%H:%M:%S", time.localtime())
                    )
                )

            elif "est-ce que tu m'écoutes" in self.check_ecout:
                self.get_stream().stop_stream()
                self.mode_prompt = False
                lire_haute_voix(
                    self.get_synonymsOf("oui je suis toujours à l'écoute <kiki>")
                )

            elif "lancer une application" in self.check_ecout:
                self.get_stream().stop_stream()
                self.mode_prompt = False
                if any(
                    keyw in self.check_ecout
                    for keyw in ["internet", "chrome", "google"]
                ):
                    lancer_search_chrome(
                        questionOuverte(
                            "Que voulez vous chercher ?",
                        ).replace(" ", "+")
                    )
                else:
                    lancer_chrome(
                        tester_appelation(
                            questionOuverte(
                                "laquelle ?",
                            )
                        )
                        or ""
                    )

            elif any(
                keyword in self.check_ecout for keyword in ["effacer", "supprimer"]
            ) and any(
                keyword in self.check_ecout
                for keyword in ["conversation", "discussion"]
            ):
                if "historique" in self.check_ecout:
                    self.get_stream().stop_stream()
                    self.mode_prompt = False
                    self.delete_history()

                elif "la dernière" in self.check_ecout:
                    self.get_stream().stop_stream()
                    self.mode_prompt = False
                    self.delete_last_discussion()

                elif "les dernières" in self.check_ecout:
                    self.get_stream().stop_stream()
                    self.mode_prompt = False
                    for i in range(letters_to_number(questionOuverte("combien ?"))):
                        self.delete_last_discussion()

            elif any(
                keyword in self.check_ecout
                for keyword in ["conversation", "discussion"]
            ):
                if any(
                    keyword in self.check_ecout
                    for keyword in ["la liste des", "historique"]
                ):
                    self.get_stream().stop_stream()
                    self.mode_prompt = False
                    lire_haute_voix("Voici")
                    self.display_history()

                elif "la dernière" in self.check_ecout:
                    self.get_stream().stop_stream()
                    self.mode_prompt = False

                    _conversation = self.responses[len(self.responses) - 1]
                    _last_discussion: Conversation = self.nametowidget(_conversation)

                    if "affiche" in self.check_ecout:
                        _last_discussion.affiche_fenetre_agrandie()
                    if "archive" in self.check_ecout:
                        _last_discussion.create_pdf()
                    elif any(
                        keyword in self.check_ecout
                        for keyword in ["lis-moi", "lis moi"]
                    ):
                        lire_haute_voix(
                            f"Contenu de la dernière conversation sur un total de {self.responses.__len__()} conversations enregistrées. "
                            + _last_discussion.get_ai_response()
                        )

                elif "une" in self.check_ecout:
                    zenumber: int = letters_to_number(
                        questionOuverte(
                            "laquelle ?",
                        )
                    )
                    nb_conversations = len(self.responses)
                    if zenumber <= nb_conversations:
                        if "affiche" in self.check_ecout:
                            _conversation = self.responses[zenumber - 1]
                            _discussion: Conversation = self.nametowidget(_conversation)
                            _discussion.affiche_fenetre_agrandie()
                        elif "archive" in self.check_ecout:
                            _discussion.create_pdf()
                        elif any(
                            keyword in self.check_ecout
                            for keyword in ["lis-moi", "lis moi", "dis-moi", "dis moi"]
                        ):
                            _last_discussion.lire()
                        self.mode_prompt = False

                    else:
                        self.mode_prompt = False
                        lire_haute_voix(
                            "je suis désolé mais il n'y a pas plus de "
                            + str(nb_conversations)
                            + " conversations en mémoire"
                        )

            elif (
                any(
                    keyword in self.check_ecout
                    for keyword in ["les actualités", "les informations"]
                )
                and "affiche" in self.check_ecout
            ):
                if "toutes" in self.check_ecout:
                    self.get_stream().stop_stream()
                    for liste_rss in URL_ACTU_GLOBAL_RSS:

                        if "le monde informatique" in liste_rss["title"].lower():
                            feed_rss = my_feedparser_rss.le_monde_informatique(
                                liste_rss["content"].split(" | ")
                            )
                        elif "global_search" in liste_rss["title"].lower():

                            feed_rss = my_feedparser_rss.generic_search_rss(
                                rss_url=liste_rss["content"].split(" | "),
                                nombre_items=10,
                            )
                        else:
                            feed_rss = my_feedparser_rss.lemonde(
                                liste_rss["content"].split(" | ")
                            )

                        self.mode_prompt = False
                        for category in feed_rss:
                            _response = self.send_prompt(
                                content_discussion=make_resume(category),
                                necessite_ai=True,
                                grorOrNot=False,
                            )
                else:
                    self.get_stream().stop_stream()
                    self.mode_prompt = False
                    final_list = [item["title"] for item in RULS_RSS]
                    _c, _t = self.display_listbox_actus(final_list)
            elif "donne-moi les infos" in self.check_ecout:
                self.get_stream().stop_stream()
                self.mode_prompt = False
                _motcle, articles = await self.recup_informations(
                    letters_to_number(
                        questionOuverte(
                            "combien d'articles souhaitez vous que je tente de récupèrer ?",
                        )
                    )
                )
                if (
                    questionOuiouNon(
                        "voulez-vous que je lise ce que j'ai trouvé sur la recherche ?",
                    )
                    and isinstance(articles, list)
                    and articles.__len__()
                ):
                    for article in articles:
                        print(article.title)
                        print(article.description)
                        print(article.content)

                        self.entree_prompt_principal.insert_markdown(
                            "# " + article.title
                        )
                        self.entree_prompt_principal.insert_markdown(
                            "## " + article.description
                        )
                        self.entree_prompt_principal.insert_markdown(article.content)

                    for article in articles:
                        lire_haute_voix(
                            translate_it(
                                article.title
                                + " "
                                + article.description
                                + " "
                                + article.content
                            )
                        )

            elif "faire une recherche web sur " in self.check_ecout:
                self.get_stream().stop_stream()
                self.mode_prompt = False
                self.check_ecout = self.check_ecout.replace(
                    " faire une recherche web sur", "\nrechercher sur le web : "
                )

                _websearching = self.send_prompt(
                    self.check_ecout, necessite_ai=True, grorOrNot=False
                )
                await self.check_before_read(_websearching)

            elif any(
                keyword in self.check_ecout for keyword in ["fin de", "ferm", "termin"]
            ):
                if "la session" in self.check_ecout:
                    # sortie de la boucle des commandes vocales
                    self.get_stream().stop_stream()
                    self.entree_prompt_principal.configure(
                        bg=from_rgb_to_tkColors(LIGHT0), fg=from_rgb_to_tkColors(DARK3)
                    )
                    self.bouton_commencer_diction.configure(
                        bg=from_rgb_to_tkColors(DARK3)
                    )
                    self.mode_prompt = False

                    self.bouton_commencer_diction.configure(
                        image=self.image_button_diction2,  # type: ignore
                        bg=from_rgb_to_tkColors((182, 78, 20)),
                    )
                    self.bouton_commencer_diction.update()

                    lire_haute_voix(
                        "merci. Pour ré-activer le mode commande vocales, il s'uffit de demander"
                    )
                    break

            elif "lis-moi systématiquement tes réponses" in self.check_ecout:
                self.get_stream().stop_stream()
                self.mode_prompt = False
                self.set_ok_to_Read(True)
                lire_haute_voix("c'est noté")

            elif "arrêtez la lecture systématique des réponses" in self.check_ecout:
                self.get_stream().stop_stream()
                self.mode_prompt = False
                self.set_ok_to_Read(False)
                lire_haute_voix("c'est noté")

            elif "gérer les préférences" in self.check_ecout:
                self.get_stream().stop_stream()
                nbmot: int | bool = letters_to_number(
                    questionOuverte(
                        "à partir de combien de mots dois je déclencher ma réponse ?",
                    )
                )
                if not nbmot:
                    self.nb_mots = 4
                elif isinstance(nbmot, int):
                    self.nb_mots = nbmot
                _question_validation = questionOuiouNon(
                    "souhaitez vous une validation orale de vos prompt ?",
                )
                _question_ok_to_read = questionOuiouNon(
                    "souhaitez vous une réponse orale de vos prompt ?",
                )
                self.setValide(valide=True if _question_validation else False)
                self.set_ok_to_Read(ok_to_Read=True if _question_ok_to_read else False)

                self.mode_prompt = False
                lire_haute_voix("c'est noté pour " + str(self.nb_mots) + " mots")

            elif "la validation orale" in self.check_ecout:
                if any(
                    keyword in self.check_ecout
                    for keyword in ["active", "activer", "activez"]
                ):
                    self.get_stream().stop_stream()
                    self.mode_prompt = False
                    self.setValide(True)
                    lire_haute_voix("c'est noté")

                elif any(
                    keyword in self.check_ecout
                    for keyword in ["stopper", "arrêter", "arrêtez"]
                ):
                    self.get_stream().stop_stream()
                    self.mode_prompt = False
                    self.setValide(False)
                    lire_haute_voix("c'est noté")
            if self.mode_prompt and self.check_ecout.split().__len__() >= self.nb_mots:
                self.get_stream().stop_stream()

                if self.getValide():
                    result = questionOuiouNon(
                        "avez vous terminé ?",
                    )

                    if "annulé" == result:
                        self.get_engine().Reset()
                        lire_haute_voix("ok")

                    elif result:
                        _response = self.send_prompt(
                            reserve + "\n" + self.check_ecout,
                            necessite_ai=True,
                            grorOrNot=True,
                        )
                        await self.check_before_read(_response)
                        reserve = str()

                    elif not result:
                        reserve += "\n" + self.check_ecout
                        self.check_ecout = str()

                        lire_haute_voix("continuez")

                    del result

                else:
                    _response = self.send_prompt(
                        self.check_ecout, necessite_ai=True, grorOrNot=True
                    )

                    await self.check_before_read(_response)

            try:
                self.get_stream().start_stream()
            except NameError as nerr:
                print(nerr)

        return content_saved_discussion

    async def recup_infos(self):
        await self.recup_informations(20)

    async def recup_informations(self, max_article_a_recup: int = 10):
        """
        * récupère les motclés écrits dans motcle_widget sinon,
        * demande oralement à l'utilisateur de donner un motcle pour la recherche
        d'actualités

        """

        async def insert_article_to_grande_fenetre(motcle: str):
            if isinstance(rechercheArticles, RechercheArticles):
                self.searchHystory.append(rechercheArticles)
                t = StoppableThread(
                    target=await rechercheArticles.insertContentToGrandeFentre(
                        motcles=motcle, grandeFenetre=self.grandeFenetre
                    ),
                )
                t.name="find_articles"
                threads_outils.append(t)
                t.start()

        self.grandeFenetre = GrandeFenetre(tk.Toplevel(None))
        if len(self.get_motcles()):
            for element in self.get_motcles():
                mot, nb = element.split(":")
                rechercheArticles: RechercheArticles = await self.extract_infos(
                    mot, int(nb) or max_article_a_recup
                )
                await insert_article_to_grande_fenetre(motcle=mot)

            return rechercheArticles.articles
        else:
            motcle = questionOuverte(
                "sur quel sujet voulez-vous que j'oriente mes recherches ?",
            )
            if motcle == "les sujets d'actualité":
                lire_haute_voix("Très bien, je récupère les actus en général")
                motcle = str()
            else:
                lire_haute_voix("Très bien, je récupère tout sur " + motcle)

            # récupération des titres du jour
            rechercheArticles = await self.extract_infos(motcle, max_article_a_recup)

            lire_haute_voix(
                f"j'ai trouvé {rechercheArticles.articles.__len__()} articles"
            )

            await insert_article_to_grande_fenetre(motcle=motcle)

            return motcle, rechercheArticles.articles

    async def extract_infos(self, subject, max_article_a_recup: int):
        """
        * Transforme le texte récupéré en un **objet JSON**
        * instancie un objet rechercheArticles contenant tous les résultats
        de l'objet json
        * Pour chacun des résultats de recherche Valide, instancie un objet article et l'ajoute
        à la liste des articles de l'objet rechercheArticles
        * retourne l'objet rechercheArticle actualisé
        """
        _responses = getNewsApi(subject)
        # _response_rss = my_feedparser_rss.lemondeAfrique([subject])
        # print(f"response_rss: {_response_rss}")
        # # _response_rss = my_feedparser_rss.feedparser.parse("https://www.lemonde.fr/" + subject + "/rss_full.xml")
        # _response = self.send_prompt(
        #     content_discussion=make_resume(_response_rss),
        #     necessite_ai=True,
        #     grorOrNot=False,
        # )
        # _response_rss_in_text = await self.asking()
        # print(f"response_rss_in_text: {_response_rss_in_text}")
        # resultat += entry.title_detail["value"] + "\n"
        # rubrique += translate_it(resultat)

        rechercheArticles = RechercheArticles(
            status=_responses.json()["status"],
            articles=[],
            totalResults=_responses.json()["totalResults"],
        )

        for n, article in enumerate(_responses.json()["articles"]):
            if n >= max_article_a_recup:
                break
            if not "removed" in str(article["title"]).lower():
                _transfert = Article(
                    source=article["source"],
                    author=article["author"],
                    title=article["title"],
                    description=article["description"],
                    url=article["url"],
                    urlToImage=article["urlToImage"],
                    publishedAt=article["publishedAt"],
                    content=article["content"],
                    image=await downloadimage(article["urlToImage"], 600),
                )
                rechercheArticles.articles.append(_transfert)
                print(str(n) + "/" + str(max_article_a_recup) + " ; ")

        return rechercheArticles

    async def save_to_history(self, fenetre_name: str, question: str, ai_response: str):
        """
        #### crée une sauvegarde des anciens échanges:
        Lorsque les conversations sont effacées de la fenêtre scrollable,
        la conversation correspondande est effacée aussi de la liste.
        ### A partir de (MAX_HISTORY=15) conversations,
        ### on fait un résumé des anciennes conversations
        cela permet de gerer la continuite de la conversation avec
        une certaine profondeur (à la discrétions de l'utilisateur) tout
        en évitant d'engorger la mémoire et les tokens utilisé
        """
        prompt = question[:499] if len(question) >= 500 else question
        _response = ai_response[:499] if len(ai_response) >= 500 else ai_response
        longueur = len(self.get_prompts_history())

        # A partir de 15 conversations,
        ## on fait un résumé des 10 anciennes conversations (MAX_HISTORY=15)
        if longueur >= MAX_HISTORY:
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
            if questionOuverte(
                "voulez-vous que je vous lise ce résumé ?",
            ):
                lire_haute_voix("Résumé des conversations précédente\n"+conversation_resumee)

        # Ajout de cette conversation dans la listes générale des conversations
        self.get_prompts_history().append(
            {
                "fenetre_name": fenetre_name,
                "prompt": prompt,
                "response": str(ai_response),
            },
        )

    async def check_before_read(self, response_to_read):
        """
        demande une confirmation avant de lire le résultat de la requette à haute voix
        """
        if self.get_ok_to_Read():
            lire_haute_voix(response_to_read)
        else:
            lire_haute_voix("voici !")

    # bubble aitable make workflow

    def recup_inf(self):

        this_thread = StoppableThread(
            target=lambda: create_asyncio_task(
                async_function=self.recup_informations(20)
            )
        )
        this_thread.name = "recup_infos"
        this_thread.start()
        threads_outils.append(this_thread)

    def attentif(self):
        """
        ### Méthode d'écoute attentive de ce qu'il se passe dans le micro
        * récupération du resultat et encapsulation dans un objet JSON
        * retourne la partie text de l'objet JSON pour traitement ou un texte VIDE
        """

        try:
            data_real_pre_vocal_command = self.get_stream().read(
                num_frames=8192, exception_on_overflow=False
            )

            if self.get_engine().AcceptWaveform(data_real_pre_vocal_command):

                # récupération du resultat et encapsulation dans un objet JSON
                from_data_pre_command_vocal_to_object_text = json.loads(
                    self.get_engine().Result()
                )

                self.bouton_commencer_diction.flash()
                # on renvoi la partie text de l'objet JSON
                text_pre_vocal_command: str = (
                    from_data_pre_command_vocal_to_object_text["text"]
                )
                return text_pre_vocal_command.lower()
            else:
                return ""
        except:
            return (
                simpledialog.askstring(
                    title="pas de micro", prompt="entrez votre commande"
                )
                or ""
            )

    def delete_last_discussion(self):
        """
        efface la dérnière discussion
        """
        widget: tk.Widget = self.nametowidget(self.responses.pop())
        widget.destroy()

    def delete_history(self):
        """
        supprime l'historique des conversations,
        """
        while self.responses.__len__() > 0:
            self.delete_last_discussion()

        lire_haute_voix("historique effacé !")

    def display_help(self) -> str:
        """
        affiche une fenetre d'aide
        """
        frame = tk.Toplevel(name="fenetre_aide")

        self.help_infos = SimpleMarkdownText(
            master=frame,
            width=len(max(LIST_COMMANDS, key=len)),
        )
        scrollbar_listbox = tk.Scrollbar(frame)
        scrollbar_listbox.configure(command=self.help_infos.yview)

        self.help_infos.pack(side=tk.LEFT, fill="both")

        for item in LIST_COMMANDS:
            self.help_infos.insert_markdown(item)

        self.help_infos.configure(
            background=from_rgb_to_tkColors((40, 0, 40)),
            foreground=from_rgb_to_tkColors(LIGHT2),
            yscrollcommand=scrollbar_listbox.set,
            padx=20,
            pady=10,
            wrap="word",
            state="disabled",
        )

        scrollbar_listbox.pack(side=tk.RIGHT, fill="both")

        _sortie = self.help_infos.bind("<<ListboxSelect>>", func=self.lire_commande)
        return _sortie

    def display_listbox_actus(self, final_list):
        """
        ouvre une listbox avec toute les catégories d'informations disponibles à la recherche
        chaque clic appelle une focntion de recherche de la catégorie en question : demander_actu(),
        retourn self.get_submission() initialisée auparavant dans demander_actu()
        """
        try:
            frame = tk.Toplevel(name="list_actu")
            _list_box = tk.Listbox(master=frame, width=len(max(final_list, key=len)))
            scrollbar_listbox = tk.Scrollbar(frame)
            scrollbar_listbox.configure(command=_list_box.yview)

            _list_box.pack(side=tk.LEFT, fill="both")

            for item in final_list:
                _list_box.insert(tk.END, item)

            _list_box.configure(
                background=from_rgb_to_tkColors(LIGHT3),
                foreground=from_rgb_to_tkColors(DARK3),
                yscrollcommand=scrollbar_listbox.set,
            )

            scrollbar_listbox.pack(side=tk.RIGHT, fill="both")

            _ = _list_box.bind("<<ListboxSelect>>", func=self.lancement_infos)

        except:
            lire_haute_voix("oups problème de liste d'information")
        finally:
            text_vocal_command = str()
        return self.get_submission(), text_vocal_command

    def lancement_infos(self, evt):
        _thread = StoppableThread(target=lambda:create_asyncio_task(self.demander_actu(evt)))
        _thread.name = "demande_actu"
        _thread.start()
        threads_outils.append(_thread)

    def marge_text(self, texte):
        long_text = len(texte)
        if long_text > 10:
            marge = int(long_text - (long_text / 4))
            print(
                (
                    texte.lower()[: int((long_text / 4))]
                    + " . . . "
                    + texte.lower()[marge:]
                )
                if long_text > 10
                else texte.lower()
            )
        else:
            print(texte)

    def send_prompt(
        self, content_discussion, necessite_ai: bool, grorOrNot: bool
    ) -> str:
        """
        cette méthode re-travaille le texte entrant selon qu'il doit être requestionné ou non
        voir le booléen **necessite_ai**
        """
        self.set_submission(content=content_discussion)
        self.entree_prompt_principal.clear_text()
        self.entree_prompt_principal.insert_markdown(mkd_text=content_discussion)
        self.save_to_submission()

        # ask question to AI and get (response,timing)
        if necessite_ai:
            if grorOrNot:
                response, timing = self.demander_ai_groq()
            else:
                response, timing = self.demander_ai()

        # check if exist else initialize it
        if not self.fenetre_scrollable.winfo_exists():
            self.fenetre_scrollable = FenetreScrollable(self)

        # ajoute la réponse à la fenetre scrollable
        self.addthing(
            _timing=timing if necessite_ai else 0,
            agent_appel=self.get_client(),
            simple_text=content_discussion,
            ai_response=response if necessite_ai else content_discussion,
            model=self.get_model(),
            submit_func=self.soumettre,
        )

        return response if necessite_ai else content_discussion

    def demander_ai_groq(self) -> Tuple[str, float]:
        response, timing = ask_to_ai(
            agent_appel=self.get_client(),
            prompt=self.get_submission(),
            model_to_use=self.get_model(),
            motcle=self.get_motcles(),
            p_history=self.get_prompts_history(),
        )
        return str(response), timing

    def demander_ai(self) -> Tuple[str, float]:
        """vérifie aussi le texte pour faire des recherches web"""
        response, timing = ask_to_ai(
            self.get_client(),
            self.get_submission(),
            model_to_use=self.get_model(),
            motcle=self.get_motcles(),
            p_history=self.get_prompts_history(),
        )

        return str(response), timing

    def go_submit(self, _evt):
        self.soumettre()

    def prompt_history_to_textlines(self, history) -> list:
        sortie = []
        for element in history:
            sortie.append(
                str(
                    datetime.now().ctime()
                    + "\n"
                    + "NameOfPrompt:: "
                    + element["fenetre_name"]
                    + "\n"
                    + "Prompt:: "
                    + element["prompt"]
                    + "\n"
                    + "Response:: "
                    + element["response"]
                    + "\n"
                )
            )
        return sortie

    async def asking(self) -> str:
        if self.get_debride():
            self.set_submission(" \n en mode débridé \n" + self.get_submission())

        response_ai, _timing = ask_to_ai(
            agent_appel=self.get_client(),
            prompt=self.get_submission(),
            model_to_use=self.get_model(),
            motcle=self.get_motcles(),
            p_history=self.get_prompts_history(),
        )
        readable_ai_response = str(response_ai)
        self.set_ai_response(readable_ai_response)

        self.addthing(
            _timing=_timing,
            agent_appel=self.get_client(),
            simple_text=self.entree_prompt_principal.get_text(),
            ai_response=self.get_ai_response(),
            model=self.get_model(),
            submit_func=self.soumettre,
        )

        return readable_ai_response

    def load_txt(self):
        try:
            file_to_read = filedialog.askopenfile(
                parent=self,
                title="ouvrir un txt",
                defaultextension="txt",
                mode="r",
                initialdir=".",
            )
            print(file_to_read.name)  # type: ignore
            resultat_txt = read_text_file(file_to_read.name)  # type: ignore
            lire_haute_voix("Fin de l'extraction")
            # on prepare le text pour le présenter à la méthode insert_markdown
            # qui demande un texte fait de lignes séparées par des \n
            # transforme list[str] -> str
            self.entree_prompt_principal.insert_markdown(mkd_text="".join(resultat_txt))

        except:
            messagebox("Problème avec ce fichier txt")  # type: ignore

    def load_and_affiche_txt(self):
        resultat_txt: str | None = load_txt(self)
        self.entree_prompt_principal.insert_markdown(mkd_text=resultat_txt)

    def load_and_affiche_pdf(self):
        resultat_txt: str = load_pdf(self)
        self.entree_prompt_principal.insert_markdown(mkd_text=resultat_txt)

    def paste_clipboard(self):
        self.entree_prompt_principal.clear_text()
        self.entree_prompt_principal.insert_markdown(self.clipboard_get())

    def clear_entree_prompt_principal(self):
        self.entree_prompt_principal.clear_text()

    def traite_listbox(self, list_to_check: list) -> tk.Listbox:
        frame = tk.Toplevel(name="list_ia")
        frame.grid_location(self.winfo_x() + 150, self.winfo_y() + 130)
        _list_box = tk.Listbox(
            master=frame,
            font=self.default_font,
            width=100,
        )
        scrollbar_listbox = tk.Scrollbar(frame)
        scrollbar_listbox.configure(command=_list_box.yview)

        _list_box.pack(side=tk.LEFT, fill="both")
        for item in list_to_check:
            _list_box.insert(tk.END, item)
        _list_box.configure(
            background="red",
            foreground=from_rgb_to_tkColors(DARK3),
            yscrollcommand=scrollbar_listbox.set,
        )
        scrollbar_listbox.pack(side=tk.RIGHT, fill="both")

        return _list_box

    def charge_preprompt(self, evt: tk.Event):
        """gère la sélection d'un élément dans une listebox Tkinter,
        récupère la valeur sélectionnée, obtient un préprompt correspondant,
        l'ajoute à une application et affiche un message en conséquence."""
        try:
            # Note here that Tkinter passes an event object to onselect()
            w: tk.Listbox = evt.widget
            idx = w.curselection()
            print("idx=" + str(idx) + "fin")
            index = idx[0]
            value: str = w.get(index)

            print('You selected item : "%s"' % value)

            preprompt = get_pre_prompt(
                rubrique=value,
                prompt_name=" ".join(self.get_motcles()).lower(),
            )

            self.entree_prompt_principal.insert_markdown(
                "**en mode débridé**, \n" + preprompt
            )

            lire_haute_voix("en mode débridé, " + preprompt)

        except:
            print("aucun préprompt sélectionné")
            lire_haute_voix("Oups")
        finally:
            if not w.focus_get() is None:
                w.focus_get().destroy()  # type: ignore

    def stoppeur(self):
        lecteur = lecteur_init()
        if lecteur._inLoop:
            lecteur.endLoop()
            lecteur.stop()

    def affiche_prepromts(self, list_to_check: list):
        """Diplays premprompts
        * asking for keywords about this subject
        * enregistre ces mot-cles dans l'attribut motcle de la classe app.
        * puis les insère dans <motcles_widget> de la fenetre principal
        * affiche la listebox avec la liste donnée en paramètre list_to_check
        """
        # ouvre une boite dialog et récupère la sortie
        mots_cle = (
            simpledialog.askstring(
                title="YourAssistant - pré-prompts",
                initialvalue="Python",
                prompt="Veuillez entrer le mot-clé à traiter",
            )
            or ""
        )

        # on set l'attribut motcle de la classe
        self.get_motcles().extend(mots_cle.split())

        # on récupère le tk.Entry de la fenetre principale : frame_of_buttons_principal.motcles_widget
        # on le clean et on y insère le thème récupéré par la simpledialog auparavant
        if isinstance(self.widgetMotcles, tk.Entry):
            self.widgetMotcles.select_from(0)
            self.widgetMotcles.select_to(tk.END)
            self.widgetMotcles.select_clear()
            self.widgetMotcles.insert(0, mots_cle)

        # crée et affiche une _listbox remplie avec la variable list_to_check
        _listbox: tk.Listbox = self.traite_listbox(list_to_check)

        # bind sur l'événement sélection d'un item de la liste
        # vers la fonction charge_preprompt
        _listbox.bind("<<ListboxSelect>>", func=self.charge_preprompt)

    def creer_fenetre(self, image: ImageTk.PhotoImage, msg_to_write):  # type: ignore
        """
        Méthode de création de la fenetre principale"""

        # préparation de l'espace de saisie des prompts

        self.affiche_banniere(
            image_banniere=self.image,
            slogan="... Jonathan LivingStone, dit legoeland... ",
        )

        self.master_frame_actual_prompt = tk.Canvas(
            self,
            relief="sunken",
            name="master_frame_actual_prompt",
        )
        self.master_frame_actual_prompt.pack(side=tk.BOTTOM, fill="both", expand=False)
        self.frame_of_buttons_principal = tk.Frame(
            self.master_frame_actual_prompt,
            relief="sunken",
            name="frame_of_buttons_principal",
        )
        self.frame_of_buttons_principal.configure(
            background=from_rgb_to_tkColors(DARK3)
        )
        self.frame_of_buttons_principal.pack(fill="x", expand=True)

        self.frame_actual_prompt = tk.Frame(
            self.master_frame_actual_prompt,
            relief="sunken",
            name="frame_actual_prompt",
            bg=from_rgb_to_tkColors(DARK2),
        )
        self.frame_actual_prompt.pack(fill="x", expand=True)

        self.entree_prompt_principal = SimpleMarkdownText(
            self.frame_actual_prompt,
            height=10,
            font=self.default_font,
            name="entree_prompt_principal",
        )

        self.entree_prompt_principal.widgetName = "entree_prompt_principal"

        # Attention la taille de la police, ici 10, ce parametre
        # tant à changer le cadre d'ouverture de la fenetre
        self.entree_prompt_principal.configure(
            bg=from_rgb_to_tkColors(LIGHT0),
            fg=from_rgb_to_tkColors(DARK3),
            font=self.default_font,
            wrap="word",
            padx=10,
            pady=6,
            undo=True,
        )

        self.boutton_paste_clipboard = tk.Button(
            self.frame_of_buttons_principal,
            font=self.btn_font,
            relief="flat",
            text="✔",
            fg="green",
            command=self.paste_clipboard,
        )
        self.boutton_effacer_historique = tk.Button(
            self.frame_of_buttons_principal,
            font=self.btn_font,
            relief="flat",
            text="🚫",
            fg="blue",
            bg=from_rgb_to_tkColors(LIGHT3),
            command=self.delete_history,
        )
        self.boutton_historique = tk.Button(
            self.frame_of_buttons_principal,
            font=self.btn_font,
            relief="flat",
            text="📆",
            command=self.display_history,
        )
        self.boutton_historique.pack(side="right")
        self.boutton_paste_clipboard.pack(side="right")
        self.boutton_effacer_historique.pack(side="right")
        self.scrollbar_prompt_principal = tk.Scrollbar(self.frame_actual_prompt)
        self.scrollbar_prompt_principal.pack(side=tk.RIGHT, fill="both")

        self.entree_prompt_principal.insert_markdown(
            mkd_text=msg_to_write + " **< CTRL + RETURN > pour valider.**"
        )
        self.entree_prompt_principal.focus_set()
        self.entree_prompt_principal.pack(side="right", fill="x", expand=True)
        self.entree_prompt_principal.configure(
            yscrollcommand=self.scrollbar_prompt_principal.set
        )

        self.entree_prompt_principal.bind("<Control-Return>", func=self.go_submit)

        # Création d'un champ de saisie de l'utilisateur
        self.scrollbar_prompt_principal.configure(
            command=self.entree_prompt_principal.yview, bg=from_rgb_to_tkColors(DARK2)
        )

        # Création d'un bouton pour Lire
        self.bouton_lire1 = tk.Button(
            self.frame_of_buttons_principal,
            activebackground=from_rgb_to_tkColors((255, 0, 0)),
            activeforeground=from_rgb_to_tkColors((0, 255, 255)),
            relief="flat",
            font=self.btn_font,
            text=chr(9654),
            command=self.lance_lecture,
        )
        self.bouton_lire1.configure(
            bg=from_rgb_to_tkColors(DARK3),
            fg=from_rgb_to_tkColors(LIGHT3),
            highlightbackground="red",
            highlightcolor=from_rgb_to_tkColors(LIGHT3),
            activebackground="red",
        )
        self.bouton_lire1.pack(side=tk.LEFT)

        # Création d'un bouton pour traduction_sur_place
        self.bouton_traduire_sur_place = tk.Button(
            self.frame_of_buttons_principal,
            font=self.btn_font,
            relief="flat",
            text="Translate",
            command=self.traduit_maintenant,  # type: ignore
        )
        self.bouton_traduire_sur_place.configure(
            bg=from_rgb_to_tkColors(DARK2),
            fg=from_rgb_to_tkColors(LIGHT3),
            highlightbackground="red",
            highlightcolor=from_rgb_to_tkColors(LIGHT3),
        )
        self.bouton_traduire_sur_place.pack(side=tk.LEFT)

        # Création d'un bouton pour Dicter
        self.bouton_commencer_diction = tk.Button(
            self.frame_actual_prompt,
            bg=from_rgb_to_tkColors(DARK3),
            image=self.image_button_diction1,  # type: ignore
            command=self.lance_thread_ecoute,
        )
        self.bouton_commencer_diction.pack(side=tk.LEFT, fill="x", expand=True)
        self.bouton_commencer_diction.bind("<Enter>", func=self.onEnter())
        self.bouton_commencer_diction.bind("<Leave>", func=self.onLeave())

        # Création d'un bouton pour soumetre
        self.bouton_soumetre = tk.Button(
            self.frame_of_buttons_principal,
            relief="flat",
            font=self.btn_font,
            text="🅰ℹ",
            fg="blue",
            command=self.soumettre,
        )

        self.bouton_soumetre.configure(
            bg=from_rgb_to_tkColors(LIGHT3),
            highlightbackground="blue",
            highlightcolor=from_rgb_to_tkColors(LIGHT3),
        )
        self.bouton_soumetre.pack(side=tk.LEFT)

        self.bouton_save_to_mp3 = tk.Button(
            self.frame_of_buttons_principal,
            font=self.btn_font,
            relief="flat",
            text="txt \u261B mp3",
            command=self.textwidget_to_mp3,
        )
        self.bouton_save_to_mp3.configure(
            bg=from_rgb_to_tkColors(DARK1), fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.bouton_save_to_mp3.pack(side="left")

        self.bouton_load_pdf = tk.Button(
            self.frame_of_buttons_principal,
            font=self.btn_font,
            text="📂 Pdf",
            relief="flat",
            command=self.load_and_affiche_pdf,
        )
        self.bouton_load_pdf.configure(
            bg=from_rgb_to_tkColors(DARK2), fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.bouton_load_pdf.pack(side="left")

        self.bouton_load_txt = tk.Button(
            self.frame_of_buttons_principal,
            font=self.btn_font,
            relief="flat",
            text="📂 TXT",
            command=self.load_and_affiche_txt,
        )
        self.bouton_load_txt.configure(
            bg=from_rgb_to_tkColors(DARK3), fg=from_rgb_to_tkColors((255, 255, 255))
        )
        self.bouton_load_txt.pack(side="left")

        self.widgetMotcles = tk.Entry(
            self.frame_of_buttons_principal,
            name="motcles_widget",
            relief="flat",
            width=50,
            fg="red",
            bg=from_rgb_to_tkColors(DARK3),
            font=("trebuchet", 10, "bold"),
        )
        self.button_keywords = tk.Button(
            self.frame_of_buttons_principal,
            font=self.btn_font,
            text="📌",
            relief="flat",
            background=from_rgb_to_tkColors(DARK2),
            foreground=from_rgb_to_tkColors(LIGHT3),
            command=lambda: self.affiche_prepromts(PROMPTS_SYSTEMIQUES.keys()),  # type: ignore
        )
        self.button_keywords.pack(side=tk.RIGHT, expand=False)
        self.widgetMotcles.pack(side="left", fill="x", padx=2, pady=2)

    def onLeave(self):
        self.bouton_commencer_diction.configure(bg=from_rgb_to_tkColors(DARK3))

    def onEnter(self):
        self.bouton_commencer_diction.configure(bg="yellow")

    def textwidget_to_mp3(self):
        """
        #### txt vers mp3
        Transforme le text sélectionné dans l'object de type
        SimpleMarkdownText donné en parametre en dictée mp3.
            Si rien n'est sélectionné, tout le text est traité.
        """
        obj: SimpleMarkdownText = self.entree_prompt_principal

        if None == obj.get_selection():
            # on récupère tout le contenu de l'objet
            texte_to_save_to_mp3 = obj.get("1.0", tk.END)
        else:
            texte_to_save_to_mp3 = obj.get_selection()

        if None != texte_to_save_to_mp3:
            if len(str(texte_to_save_to_mp3)) > 0:

                lire_haute_voix("transcription du texte vers un fichier mp3")
                file_name_mp3 = (
                    simpledialog.askstring(
                        parent=self,
                        prompt="Enregistrement : veuillez choisir un nom au fichier",
                        title="Enregistrer vers audio",
                    )
                    or "my_texte"
                )
                lecteur_init().save_to_file(
                    texte_to_save_to_mp3, file_name_mp3.lower() + ".mp3"
                )
                lire_haute_voix("terminé")
        else:
            print("rien à transformer")

    def replace_in_place(
        self, texte: str, index1: str, index2: str, ponctuel: bool = True
    ):
        """traduit sur place (remplacement) le texte sélectionné"""
        self.entree_prompt_principal.replace(chars=texte, index1=index1, index2=index2)

    def traduit_maintenant(self):
        self.set_timer(float(time.perf_counter_ns()))
        was_a_list = False
        try:
            # TRANSLATE IN PLACE
            texte_initial = self.entree_prompt_principal.get_selection()
            indx1 = self.entree_prompt_principal.index(tk.SEL_FIRST)
            indx2 = self.entree_prompt_principal.index(tk.SEL_LAST)

            texte_traite = traitement_du_texte(str(texte_initial))
            if isinstance(texte_traite, list):
                for element in texte_traite:
                    translated_text = str(translate_it(text_to_translate=element))
                    self.replace_in_place(
                        texte=translated_text,
                        index1=indx1,
                        index2=indx2,
                        ponctuel=False,
                    )

            else:
                translated_text = str(translate_it(text_to_translate=texte_traite))
                self.replace_in_place(
                    texte=translated_text, index1=indx1, index2=indx2, ponctuel=True
                )

        except ValueError as ve:
            # TRANSLATE COMPLETE
            texte_initial = self.entree_prompt_principal.get("1.0", tk.END)
            texte_brut_initial = texte_initial.replace("\n", " ")
            texte_traite = traitement_du_texte(texte_initial)

            if isinstance(texte_traite, list):
                sortie = str()
                for element in texte_traite:
                    translated_text = str(translate_it(text_to_translate=element))
                    sortie += "\n" + translated_text
                was_a_list = True

                timing: float = (
                    time.perf_counter_ns() - self.get_timer()
                ) / TIMING_COEF
                self.addthing(
                    _timing=timing,
                    agent_appel=self.get_client(),
                    simple_text=self.entree_prompt_principal.get_text(),
                    ai_response=sortie,
                    model=self.get_model(),
                    submit_func=self.soumettre,
                )
            elif was_a_list == True:
                translated_text = str(translate_it(text_to_translate=texte_traite))
                timing: float = (
                    time.perf_counter_ns() - self.get_timer()
                ) / TIMING_COEF
                self.addthing(
                    _timing=timing,
                    agent_appel=self.get_client(),
                    simple_text=self.entree_prompt_principal.get_text(),
                    ai_response=translated_text,
                    model=self.get_model(),
                    submit_func=self.soumettre,
                )
            else:
                translated_text = str(translate_it(text_to_translate=texte_traite))
                timing: float = (
                    time.perf_counter_ns() - self.get_timer()
                ) / TIMING_COEF
                self.addthing(
                    _timing=timing,
                    agent_appel=self.get_client(),
                    simple_text=self.entree_prompt_principal.get_text(),
                    ai_response=translated_text,
                    model=self.get_model(),
                    submit_func=self.soumettre,
                )

            print(ve)
            lire_haute_voix("fin de la traduction")

    def lance_lecture(self):
        obj: SimpleMarkdownText = self.entree_prompt_principal
        texte_to_talk = str()
        try:
            texte_to_talk = obj.get(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            texte_to_talk = obj.get("1.0", tk.END)
        finally:
            lire_haute_voix(texte_to_talk)

    def load_selected_model(self, evt: tk.Event):
        # Note here that Tkinter passes an event object to onselect()
        w: tk.Listbox = evt.widget
        try:
            index = w.curselection()[0]
            value = w.get(index)
            print('You selected item %d: "%s"' % (index, value))
            self.set_model(name_ia=str(value))
            _widget: tk.Button = self.nametowidget("cnvs1.cnvs2.btnlist")
            _widget.configure(text=value)
            lire_haute_voix("ok")
        except:
            print("aucune ia sélectionner")
            lire_haute_voix("Oups problème de listing de modèle")
        finally:
            w.focus_get().destroy()  # type: ignore

    async def demander_actu(self, evt: tk.Event):
        """
        **Flux-rss** : Méthode appelée par la listbox des catégories d'actualités.
        elle va récupérer les flux rss conrrespondants pour les envoyer en questionnement à l'AI
        via send_prompt()

        """

        # Note here that Tkinter passes an event object to onselect()
        w: tk.Listbox = evt.widget
        try:
            index = w.curselection()[0]
            value = w.get(index)
            print('You selected item %d: "%s"' % (index, value))
            content_selected = [
                item["content"] for item in RULS_RSS if item["title"].lower() == value.lower() 
            ].pop()

            print(content_selected)
            if "le monde informatique" in value.lower():
                feed_rss:list = my_feedparser_rss.le_monde_informatique(
                    content_selected.split(" | ")
                )

            elif "global_search" in value.lower():
                feed_rss:list = my_feedparser_rss.linforme(nombre_items=10)
            else:
                feed_rss:list = my_feedparser_rss.lemonde(content_selected.split(" | "))

            for subject in feed_rss:
                response = self.send_prompt(
                    content_discussion=make_resume(subject),
                    necessite_ai=True,
                    grorOrNot=True,
                )

                self.set_submission(response)
            
            lire_haute_voix("Récupération terminée")

        except Exception as e:
            lire_haute_voix("Aïe !! demande d'actualité :  ")

    def lire_commande(self, evt: tk.Event):

        # Note here that Tkinter passes an event object to onselect()
        w: tk.Listbox = evt.widget
        index = w.curselection()[0]
        value = w.get(index)
        print('You selected item %d: "%s"' % (index, value))
        lire_haute_voix(value)

    def affiche_ia_list(self, list_to_check: list):
        """
        Display a list of AI you can use
        * affiche la listebox avec la liste donnée en paramètre list_to_check
        * click on it cause model AI to change
        """
        _listbox: tk.Listbox = self.traite_listbox(list_to_check)
        _listbox.bind("<<ListboxSelect>>", func=self.load_selected_model)

    def display_history(self):
        """
        Display a list of AI you can use
        * affiche la listebox avec la liste donnée en paramètre list_to_check
        * click on it cause model AI to change
        """
        list_to_check = [element.split(".")[4:] for element in self.responses]
        _listbox: tk.Listbox = self.traite_listbox(list_to_check)

    def get_prompts_history(self) -> list:
        return self.prompts_history

    def supprimer_conversation(self, evt: tk.Event):
        conversation: Conversation = evt.widget
        print("Effacement de la conversation ::" + conversation.id + "::")
        try:
            self.responses.remove(conversation.id)
        except:
            print(f"la fentre {conversation.id} est déjà effacée")
        conversation.destroy()
        conversation.canvas_edition.destroy()
        self.fenetre_scrollable.update()

    def addthing(
        self,
        _timing,
        agent_appel,
        simple_text: str,
        ai_response: str,
        model,
        submit_func,
    ):
        """ajouter une conversation"""
        self.model = model
        fenetre_response: Conversation = Conversation(
            ai_response=ai_response,
            text=simple_text,
            master=self.fenetre_scrollable.frame,
            submit=submit_func,
            agent_appel=agent_appel,
            model_to_use=model,
            nb_conversation=self.responses.__len__(),
        )
        fenetre_response.pack(fill="x", expand=True)
        self.history.append(fenetre_response)

        self.responses.append(fenetre_response.id)

        this_thread: StoppableThread = StoppableThread(
            target=lambda: create_asyncio_task(
                async_function=self.save_to_history(
                    fenetre_response.id, simple_text, ai_response
                )
            )
        )
        this_thread.name = "save_to_history"
        this_thread.start()
        threads_outils.append(this_thread)

        fenetre_response.bind(
            "<Destroy>",
            func=self.supprimer_conversation,
        )

        fenetre_response.get_entree_response().insert_markdown(
            "_" + str(_timing)[:3] + "secondes < " + str(type(agent_appel)) + " >_\n",
        )
        fenetre_response.get_entree_response().insert_markdown(ai_response + "\n")

        fenetre_response.get_entree_question().insert_markdown(
            str(_timing)[:3] + "secondes < " + str(type(agent_appel)) + " >\n",
        )

        fenetre_response.get_entree_question().insert_markdown(simple_text + "\n")

        fenetre_response.affiche_fenetre_agrandie()

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
        for item in self.responses:
            suzi: Conversation = self.nametowidget(item)
            audrey = suzi.get_entree_question().get_text()
            julia = suzi.get_entree_response().get_text()
            print(
                suzi.widgetName
                + ":: \n-----------------------"
                + "\nPrompt:: "
                + str(audrey[:60] + "... " if len(audrey) >= 59 else audrey)
                + "Response:: "
                + str(julia[:59] + "...\n" if len(julia) >= 60 else julia + "\n")
            )
        print("************************************")
