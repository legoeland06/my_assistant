from datetime import datetime
import asyncio
import json
import random
import time
from tkinter import filedialog, messagebox, simpledialog
from typing import Any, Tuple
from groq import Groq
import ollama
from llama_index.llms.ollama import Ollama as Ola
from openai import ChatCompletion
import pyaudio
from Constants import *
import tkinter.font as tkfont
import tkinter as tk
import vosk
from PIL import Image, ImageTk
import threading

from FenetreScrollable import FenetreScrollable
from SimpleMarkdownText import SimpleMarkdownText
from StoppableThread import StoppableThread
import my_search_engine as search
import my_feedparser_rss
from secret import GROQ_API_KEY

from outils import (
    actualise_index_html,
    append_response_to_file,
    append_saved_texte,
    askToRead,
    engine_lecteur_init,
    from_rgb_to_tkColors,
    get_groq_ia_list,
    get_pre_prompt,
    initialise_conversation_audio,
    lire_haute_voix,
    load_pdf,
    load_txt,
    make_resume,
    random_je_vous_ecoute,
    read_text_file,
    traitement_du_texte,
    translate_it,
)


class FenetrePrincipale(tk.Frame):
    master: tk.Tk
    content: str
    title: str
    ia: str
    submission: str
    model_to_use: str
    streaming: pyaudio.Stream

    # moteur de reconnaissance vocale et d'écoute
    engine_model: vosk.KaldiRecognizer

    image: ImageTk
    image_link: str
    client: any = None
    ai_response: str
    timer: float
    thread: threading.Thread
    messages: list
    actual_chat_completion: ChatCompletion

    def __init__(
        self,
        # Stream audio du micro ouvert
        stream: pyaudio.Stream,
        # model ia à utiliser
        model_to_use: str,
        master,
    ):
        super().__init__(master)
        self.master = master
        self.ia = LLAMA3
        self.thread = None
        self.submission = ""
        self.fontdict = tkfont.Font(
            family=ZEFONT[0],
            size=ZEFONT[1],
            slant=ZEFONT[2],
            weight=ZEFONT[3],
        )
        self.timer: float = 0
        self.model_to_use = model_to_use
        self.streaming = stream
        self.image = ImageTk.PhotoImage(
            Image.open("banniere.jpeg").resize((BANNIERE_WIDTH, BANNIERE_HEIGHT))
        )
        self.image_link = ""
        self.content = ""
        self.motcles = []
        self.configure(padx=5, pady=5, width=96 + 10)
        self.pack()

        ##
        # phase de construction de la fenetre principale
        self.creer_fenetre(
            image=self.get_image(),
            msg_to_write="Prompt...",
        )

        self.fenetre_scrollable = FenetreScrollable(self)
        self.fenetre_scrollable.configure(width=self.master.winfo_reqwidth() - 20)
        self.fenetre_scrollable.configure(height=self.master.winfo_reqheight() - 20)
        self.fenetre_scrollable.pack(side="bottom", fill="x", expand=True)
        self.my_liste = []
        self.messages = [
            {
                "role": "user",
                "content": "Bonjour",
            },
        ]
        self.actual_chat_completion = []

    def getListOfModels(self):
        return [element["name"] for element in (ollama.list())["models"]]

    def get_actual_chat_completion(self) -> list:
        return self.actual_chat_completion

    def set_thread(self, thread: StoppableThread):
        self.thread = thread

    def get_thread(self) -> StoppableThread:
        return self.thread

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

    def set_motcles(self, motcles: list[str]):
        self.motcles = motcles

    def get_motcles(self) -> list[str]:
        return self.motcles

    def set(self, content: str):
        self.content = content

    def get(self) -> str:
        return self.content

    def set_submission(self, content: str):
        self.submission = content

    def get_submission(self) -> str:
        return self.submission

    def get_image_link(self) -> str:
        return self.image_link

    def set_image_link(self, image_link: str):
        self.image_link = image_link

    def set_model(self, name_ia: str) -> bool:
        self.model_to_use = name_ia
        lire_haute_voix("changement d'ia: " + self.model_to_use)

    def get_model(self) -> str:
        return self.model_to_use

    def get_stream(self) -> pyaudio.Stream:
        return self.streaming

    def set_engine(self, engine: vosk.KaldiRecognizer):
        """
        ### set le moteur de reconnaissance vocale
        Attention : chargement est long
        #### TODO vérifier qu'il s'agissse d'un singleton
        """
        self.engine_model = engine

    def get_engine(self) -> vosk.KaldiRecognizer:
        return self.engine_model

    def get_image(self) -> ImageTk:
        return self.image

    def set_image(self, image: ImageTk) -> bool:
        self.image = image
        return True

    def save_to_submission(self) -> bool:
        """ """
        if self.motcles_widget.get() is None:
            print("OOps, rien à sauver")
        else:
            print(self.motcles_widget.get())
        # récupère le texte contenu dans le widget_mot_clé
        speciality = self.motcles_widget.get() if len(self.motcles_widget.get()) else ""
        self.set_motcles([speciality])
        # self.get_motcles().append(speciality)

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

    def quitter(self) -> str:
        # Afficher une boîte de message de confirmation
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir quitter ?"):
            self.save_to_submission()
            self.get_thread().stop()
            self.master.destroy()
            self.destroy()
        else:
            print("L'utilisateur a annulé.")

    # open a windows
    def affiche_banniere(self, image_banniere: ImageTk, slogan, quitter_app):
        """affiche l'illustration (la bannière) et les boutons de saisie système
        * bouton quitter
        * sélection du clien Ola ou ollama...
        * sélection du modèle d'ia ...."""
        # ## PRESENTATION DU GOELAND  ####
        canvas_principal_banniere = tk.Frame(
            self, background=from_rgb_to_tkColors(DARK2), name="cnvs1"
        )
        canvas_principal_banniere.pack(fill="x", expand=True)
        # ################################
        canvas_buttons_banniere = tk.Frame(canvas_principal_banniere, name="cnvs2")
        canvas_buttons_banniere.configure(bg=from_rgb_to_tkColors(DARK3))
        canvas_buttons_banniere.pack(fill="x", expand=False)

        # Create a canvas
        canvas_image_banniere = tk.Canvas(
            canvas_principal_banniere,
            height=BANNIERE_HEIGHT,
            width=BANNIERE_WIDTH,
            background=from_rgb_to_tkColors(DARK2),
            name="canva",
        )

        # Création d'un bouton pour quitter
        bouton_quitter = tk.Button(
            canvas_buttons_banniere, text="Quitter", command=self.master.destroy
        )
        bouton_quitter.configure(
            background=from_rgb_to_tkColors(DARK3), foreground="red"
        )
        bouton_quitter.pack(side=tk.LEFT)

        bouton_Ola = tk.Button(
            canvas_buttons_banniere,
            text="Ola",
            command=lambda: self.set_client(Ola),
            highlightthickness=3,
            highlightcolor="yellow",
        )
        bouton_Ola.configure(
            background=from_rgb_to_tkColors(LIGHT3),
            foreground=from_rgb_to_tkColors(DARK3),
        )
        bouton_Ola.pack(side=tk.LEFT)

        bouton_Groq = tk.Button(
            canvas_buttons_banniere,
            text="CLient_groq",
            command=self.groq_choix_ia,
            highlightthickness=3,
            highlightcolor="yellow",
        )
        bouton_Groq.configure(
            background=from_rgb_to_tkColors(LIGHT3),
            foreground=from_rgb_to_tkColors(DARK3),
        )
        bouton_Groq.pack(side=tk.LEFT)

        bouton_Ollama = tk.Button(
            canvas_buttons_banniere,
            text="Ollama",
            command=lambda: self.set_client(
                ollama.Client(host="http://127.0.0.1:11434")
            ),
            highlightthickness=3,
            highlightcolor="yellow",
        )
        bouton_Ollama.configure(
            background=from_rgb_to_tkColors(LIGHT3),
            foreground=from_rgb_to_tkColors(DARK3),
        )
        bouton_Ollama.pack(side=tk.LEFT)

        bouton_display_list_models = tk.Button(
            canvas_buttons_banniere,
            name="btnlist",
            text="Changer d'IA",
            background="red",
            foreground=from_rgb_to_tkColors(DARK3),
            command=lambda: self.affiche_ia_list(self.getListOfModels()),
        )

        label_slogan = tk.Label(
            canvas_buttons_banniere,
            text=slogan,
            font=("Trebuchet", 8),
            fg=from_rgb_to_tkColors(LIGHT3),
            bg=from_rgb_to_tkColors(DARK2),
        )

        label_slogan.pack(side=tk.RIGHT, expand=False)
        bouton_display_list_models.pack(side=tk.RIGHT, expand=False)

        # Add the image to the canvas, anchored at the top-left (northwest) corner
        canvas_image_banniere.create_image(
            0, 0, anchor="nw", image=image_banniere, tags="bg_img"
        )
        canvas_image_banniere.pack(fill="x", expand=True)

    def affiche_ban(self):
        self.affiche_banniere(
            image_banniere=self.image,
            quitter_app=self.quitter,
            slogan="... Jonathan LivingStone, dit legoeland",
        )

    def groq_choix_ia(self):
        groq_client = Groq(api_key=GROQ_API_KEY)
        self.set_client(groq_client)
        models = get_groq_ia_list(api_key=GROQ_API_KEY)
        self.affiche_ia_list(models)

    def soumettre(self) -> str:
        if self.save_to_submission():
            this_thread = threading.Thread(target=self.submit_thread)
            lire_haute_voix(self.get_synonymsOf("un instant s'il vous plait"))
            list_of_words = self.get_submission().split()
            print("longeur du prompt:: " + str(len(list_of_words)))
            # TODO
            if len(list_of_words) >= 3000:
                new_prompt_list = traitement_du_texte(self.get_submission(), 3000)
                lire_haute_voix(
                    "le prompt est trop long, il est supérieur à 3000 tokens, il sera découpé en "
                    + str(len(new_prompt_list))
                    + " blocs"
                )
                for number, bloc in enumerate(new_prompt_list):
                    print(str(number) + " " + str(bloc))
                    self.set_submission(str(bloc))
                    threading.Thread(target=self.submit_thread).start()
                    time.sleep(1)
                    # lancement_de_la_lecture("bloc numéro " + str(number))

                    # if threading.Thread(target=self.submit_thread).isDaemon():
                    #     this_thread_splited.join()

            else:
                this_thread.start()

        else:
            messagebox.showinfo(
                message=self.get_synonymsOf("Veuillez poser au moins une question")
            )

    def lance_thread_ecoute(self):
        if self.get_thread() == None or self.get_thread().stopped():
            self.bouton_commencer_diction.flash()
            my_thread = StoppableThread(None, name="my_thread", target=self.ecouter)
            self.set_thread(my_thread)
            self.get_thread().start()

    def ecouter(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(self.dialog_ia())
        loop.run_forever()

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
                # print(str(ai_response))
            except:
                messagebox.Message("OOps, ")
                return expression
            return str(ai_response).split("\n")[
                (round(random.randint(1, 19 * 10) / 10) % 19) + 1
            ]
        return expression

    # TODO : problème ici, difficulté à arrêter le thread !!
    async def dialog_ia(self):
        lire_haute_voix(self.get_synonymsOf("Bienvenue !"))

        is_pre_vocal_command = True
        lire_haute_voix(
            self.get_synonymsOf(
                "pour activer les commandes vocales, il suffit de dire : << active les commandes vocales >>"
            )
        )
        self.get_stream().start_stream()
        content_saved_discussion = ""
        while True:
            self.bouton_commencer_diction.configure(bg="blue")
            mode_ecoute = False
            is_human_is_talking = False

            if self.get_stream().is_stopped():
                self.get_stream().start_stream()

            data_real_pre_vocal_command = self.get_stream().read(
                num_frames=8192, exception_on_overflow=False
            )

            if self.get_engine().AcceptWaveform(data_real_pre_vocal_command):
                from_data_pre_command_vocal_to_object_text = json.loads(
                    self.get_engine().Result()
                )
                self.bouton_commencer_diction.flash()

                text_pre_vocal_command: str = (
                    from_data_pre_command_vocal_to_object_text["text"]
                )

                welcoming = True
                if len(text_pre_vocal_command):

                    if "afficher de l'aide" in text_pre_vocal_command.lower():
                        text_pre_vocal_command = self.affiche_aide()

                    elif "ferme l'application" == text_pre_vocal_command.lower():
                        # data_real_pre_vocal_command = None
                        # from_data_vocal_command_to_object_text = None
                        _, _, text_pre_vocal_command, _ = (
                            initialise_conversation_audio()
                        )
                        is_pre_vocal_command = True
                        self.get_stream().stop_stream()
                        self.get_thread().stop()
                        lire_haute_voix(
                            "ok, vous pouvez réactiver l'observeur audio en appuyant sur le bouton rouge"
                        )
                        self.bouton_commencer_diction.configure(bg="red")
                        append_saved_texte(
                            file_to_append="saved_text",
                            readable_ai_response=content_saved_discussion,
                        )
                        content_saved_discussion = ""
                        break

                    elif (
                        "active le mode audio" in text_pre_vocal_command.lower()
                        or "activer le mode audio" in text_pre_vocal_command.lower()
                        or "active les commandes vocales"
                        in text_pre_vocal_command.lower()
                        or "activer les commandes vocales"
                        in text_pre_vocal_command.lower()
                    ):
                        lire_haute_voix(
                            self.get_synonymsOf(
                                "très bien, pour sortir de ce mode, dites : fin de la session"
                            )
                        )
                        (
                            welcoming,
                            is_pre_vocal_command,
                            text_pre_vocal_command,
                            _,
                        ) = initialise_conversation_audio()
                        append_saved_texte(
                            file_to_append="saved_text",
                            readable_ai_response=content_saved_discussion,
                        )
                        content_saved_discussion = ""
                        self.bouton_commencer_diction.configure(bg="green")

                    else:
                        content_saved_discussion += (
                            text_pre_vocal_command.lower() + "\n"
                        )

            while not is_pre_vocal_command:
                if welcoming:
                    self.get_stream().start_stream()
                    # on peut maintenant réouvrir la boucle d'audition
                    lire_haute_voix(self.get_synonymsOf("je vous écoute maintenant"))
                    # lire_haute_voix(random_je_vous_ecoute())
                    _, _, content_discussion, text_vocal_command = (
                        initialise_conversation_audio()
                    )
                    welcoming = not welcoming

                (
                    self.set_timer(time.perf_counter_ns())
                    if is_human_is_talking and mode_ecoute
                    else None
                )

                if self.get_engine().AcceptWaveform(
                    self.get_stream().read(
                        num_frames=8192, exception_on_overflow=False
                    )  # read in chunks of 4096 bytes
                ):  # accept waveform of input voice
                    # Parse the JSON result and get the recognized text

                    text_vocal_command: str = json.loads(self.get_engine().Result())[
                        "text"
                    ]

                    if "afficher de l'aide" in text_vocal_command.lower():
                        self.get_stream().stop_stream()
                        _ = self.affiche_aide()
                        (
                            welcoming,
                            is_human_is_talking,
                            text_vocal_command,
                            content_discussion,
                        ) = initialise_conversation_audio()

                    elif "quel jour sommes-nous" in text_vocal_command.lower():
                        self.get_stream().stop_stream()
                        lire_haute_voix(
                            self.get_synonymsOf(
                                "Nous sommes le " + time.strftime("%Y-%m-%d")
                            )
                        )
                        (
                            welcoming,
                            is_human_is_talking,
                            text_vocal_command,
                            content_discussion,
                        ) = initialise_conversation_audio()

                    elif "quelle heure est-il" in text_vocal_command.lower():
                        self.get_stream().stop_stream()
                        lire_haute_voix(
                            self.get_synonymsOf(
                                "il est exactement "
                                + time.strftime("%H:%M:%S", time.localtime())
                            )
                        )
                        (
                            welcoming,
                            is_human_is_talking,
                            text_vocal_command,
                            content_discussion,
                        ) = initialise_conversation_audio()

                    elif "est-ce que tu m'écoutes" in text_vocal_command.lower():
                        self.get_stream().stop_stream()
                        lire_haute_voix(
                            self.get_synonymsOf("oui je suis toujours à l'écoute kiki")
                        )
                        (
                            welcoming,
                            is_human_is_talking,
                            text_vocal_command,
                            content_discussion,
                        ) = initialise_conversation_audio()

                    elif (
                        "effacer l'historique des conversations"
                        in text_vocal_command.lower()
                        or "supprimer l'historique des conversations"
                        in text_vocal_command.lower()
                        or "effacer l'historique des discussions"
                        in text_vocal_command.lower()
                        or "supprimer l'historique des discussions"
                        in text_vocal_command.lower()
                    ):
                        self.get_stream().stop_stream()

                        # ici on supprime complètement la fenetre scrollable
                        # et tout ce qu'il y a dedans
                        for resp in self.fenetre_scrollable.responses:
                            resp.destroy()

                        self.fenetre_scrollable.responses.clear()

                        lire_haute_voix("historique effacé !")
                        (
                            welcoming,
                            is_human_is_talking,
                            text_vocal_command,
                            content_discussion,
                        ) = initialise_conversation_audio()

                    elif (
                        "effacer la dernière conversation" in text_vocal_command.lower()
                        or "effacer la dernière discussion"
                        in text_vocal_command.lower()
                    ):
                        self.get_stream().stop_stream()
                        kiki: tk.Widget = self.fenetre_scrollable.responses.pop()
                        kiki.destroy()
                        lire_haute_voix("c'est fait !")
                        (
                            welcoming,
                            is_human_is_talking,
                            text_vocal_command,
                            content_discussion,
                        ) = initialise_conversation_audio()

                    elif (
                        "afficher la liste des conversations"
                        in text_vocal_command.lower()
                        or "afficher l'historique des conversations"
                        in text_vocal_command.lower()
                        or "montre-moi les conversations" in text_vocal_command.lower()
                    ):
                        self.get_stream().stop_stream()
                        lire_haute_voix("Voici")
                        self.boutton_historique.invoke()

                        (
                            welcoming,
                            is_human_is_talking,
                            text_vocal_command,
                            content_discussion,
                        ) = initialise_conversation_audio()

                    elif (
                        "afficher toutes les actualités" in text_vocal_command.lower()
                        or "affiche toutes les actualités" in text_vocal_command.lower()
                    ):
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

                            response = self.envoyer_audio_prompt(
                                content_discussion=make_resume(feed_rss),
                                necessite_ai=True,
                                grorOrNot=False,
                            )

                        (
                            welcoming,
                            is_human_is_talking,
                            text_vocal_command,
                            content_discussion,
                        ) = initialise_conversation_audio()

                    elif (
                        "afficher les actualités" in text_vocal_command.lower()
                        or "afficher des actualités" in text_vocal_command.lower()
                        or "afficher des informations" in text_vocal_command.lower()
                        or "afficher les informations" in text_vocal_command.lower()
                        or "affiche les actualités" in text_vocal_command.lower()
                        or "affiche des actualités" in text_vocal_command.lower()
                        or "affiche les informations" in text_vocal_command.lower()
                        or "affiche des informations" in text_vocal_command.lower()
                    ):
                        self.get_stream().stop_stream()
                        if not self.fenetre_scrollable.winfo_exists:
                            self.fenetre_scrollable = FenetreScrollable(self)
                        final_list = [item["title"] for item in RULS_RSS]
                        for truc in final_list:
                            print(truc)

                        content_discussion, text_vocal_command = (
                            self.affiche_list_informations(final_list)
                        )
                        askToRead(
                            self.get_engine(),
                            self.get_stream(),
                            self.envoyer_audio_prompt(
                                content_discussion, necessite_ai=True, grorOrNot=True
                            ),
                        )

                        (
                            welcoming,
                            is_human_is_talking,
                            text_vocal_command,
                            content_discussion,
                        ) = initialise_conversation_audio()

                    elif "faire une recherche web sur " in text_vocal_command.lower():
                        self.get_stream().stop_stream()
                        text_vocal_command = text_vocal_command.replace(
                            " faire une recherche web sur", "\nrechercher sur le web : "
                        )

                        content_discussion += text_vocal_command
                        response = self.envoyer_audio_prompt(
                            content_discussion, necessite_ai=True, grorOrNot=False
                        )
                        (
                            welcoming,
                            is_human_is_talking,
                            text_vocal_command,
                            content_discussion,
                        ) = initialise_conversation_audio()

                    elif "fin de la session" in text_vocal_command.lower():
                        # sortie de la boucle d'audition
                        self.get_stream().stop_stream()

                        welcoming, _, text_vocal_command, content_discussion = (
                            initialise_conversation_audio()
                        )
                        is_pre_vocal_command = True
                        lire_haute_voix(
                            "merci. Pour ré-activer le mode commande vocales, il s'uffit de demander"
                        )
                        self.bouton_commencer_diction.configure(bg="red")

                    elif text_vocal_command.lower() != "":
                        mode_ecoute = True
                        is_human_is_talking = True
                        content_discussion += "\n" + text_vocal_command
                        print("texte reconnu : " + text_vocal_command.lower())

                        self.set_timer(time.perf_counter_ns())

                    if (
                        # (time.perf_counter_ns() - self.get_timer()) / TIMING_COEF
                        # > 0.05  # en secondes
                        # and
                        is_human_is_talking
                        and mode_ecoute
                        and content_discussion.split().__len__() > 0
                    ):
                        mode_ecoute = False
                        self.get_stream().stop_stream()

                        # ici on affiche le temps de blanc avant de commencer à lui parler
                        # à partir du moment où il dit "à vous"

                        print(
                            " :: "
                            + str(
                                (time.perf_counter_ns() - self.get_timer())
                                / TIMING_COEF
                            )
                            + " ::secondes "
                        )

                        askToRead(
                            self.get_engine(),
                            self.get_stream(),
                            self.envoyer_audio_prompt(
                                content_discussion, necessite_ai=True, grorOrNot=True
                            ),
                        )

                        # efface le fil de discussion
                        (
                            welcoming,
                            is_human_is_talking,
                            text_vocal_command,
                            content_discussion,
                        ) = initialise_conversation_audio()

        return "Future is done!"

    def affiche_aide(self) -> str:
        # for item in LIST_COMMANDS:
        #     print(item)

        frame = tk.Tk()

        _list_box = tk.Listbox(
            master=frame,
            height=len(LIST_COMMANDS),
            width=len(max(LIST_COMMANDS, key=len)),
        )
        scrollbar_listbox = tk.Scrollbar(frame)
        scrollbar_listbox.configure(command=_list_box.yview)

        _list_box.pack(side=tk.LEFT, fill="both")

        for item in LIST_COMMANDS:
            _list_box.insert(tk.END, item)

        _list_box.configure(
            background=from_rgb_to_tkColors(LIGHT3),
            foreground=from_rgb_to_tkColors(DARK3),
            yscrollcommand=scrollbar_listbox.set,
        )

        scrollbar_listbox.pack(side=tk.RIGHT, fill="both")

        _sortie = _list_box.bind("<<ListboxSelect>>", func=self.lire_commande)
        frame.mainloop()
        return _sortie

    def affiche_list_informations(self, final_list):
        try:
            frame = tk.Tk()
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

            _ = _list_box.bind("<<ListboxSelect>>", func=self.demander_actu)

            frame.mainloop()
        except:
            lire_haute_voix("oups problème de liste d'information")
        finally:
            _, _, text_vocal_command, content_discussion = (
                initialise_conversation_audio()
            )
        return self.get_submission(), text_vocal_command

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

    def envoyer_audio_prompt(
        self, content_discussion, necessite_ai: bool, grorOrNot: bool
    ) -> str:
        self.set_submission(content=content_discussion)
        self.entree_prompt_principal.clear_text()
        self.entree_prompt_principal.insert_markdown(mkd_text=content_discussion)
        self.save_to_submission()

        if necessite_ai:
            if grorOrNot:
                response, timing = self.demander_ai_groq()
            else:
                response, timing = self.demander_ai()
        # ajoute la réponse à la fenetre scrollable
        if not self.fenetre_scrollable.winfo_exists():
            self.fenetre_scrollable = FenetreScrollable(self)

        self.fenetre_scrollable.addthing(
            _timing=timing if necessite_ai else 0,
            agent_appel=self.get_client(),
            simple_text=self.entree_prompt_principal.get_text(),
            ai_response=response if necessite_ai else content_discussion,
            model=self.get_model(),
            submit_func=self.soumettre,
        )

        return response if necessite_ai else content_discussion

    def demander_ai_groq(self) -> Tuple[str, float]:
        response, timing = self.ask_to_Groq(
            agent_appel=self.get_client(),
            prompt=self.get_submission(),
            model_to_use=self.get_model(),
        )
        return response, timing

    def demander_ai(self) -> Tuple[str, float]:
        """vérifie aussi le texte pour faire des recherches web"""
        response, timing = self.ask_to_ai(
            self.get_client(), self.get_submission(), self.get_model()
        )

        return response, timing

    def submit_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(loop.create_task(self.asking()))
        loop.close()

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
        sortie

    def lancer_chrome(self, word_to_search: str) -> subprocess.Popen[str]:
        link_search = "https://www.google.fr/search?q="

        return subprocess.Popen(
            GOOGLECHROME_APP + link_search + word_to_search,
            text=True,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def petite_recherche(self, term: str):
        # TODO : récupérer le mot dans le prompt directement
        # en isolant la ligne et en récupérant tout ce qu'il y a après
        # avoir identifier les mots clés "recherche web : "
        expression_found = (term.split(" : ")[1]).replace(" ", "+")
        # resultat_de_recherche = str(self.lancer_chrome(expression_found))

        # on execute cette recherche sur le web
        # avec l'agent de recherche search.main()
        lire_haute_voix("recherche web " + term.split(" : ")[1])
        search_results: list = search.main(expression_found)

        goodlist = "\n".join(
            [
                str(element["snippet"] + "\n" + element["formattedUrl"] + "\n")
                for element in search_results
            ]
        )
        return goodlist

    def check_content(self, content: str):
        """
        ### check the content
        Verify some keywords like :
            << rechercher sur le web : >>
            << en mode débridé >>

            @param: content type str

            @return: content type str ,
            @return: isAskToDebride type bool,
            @return: timing type float
        """
        result_recherche = []
        isAskToDebride = False
        for line in [line for line in content.splitlines() if line.strip()]:
            # si on a trouvé la phrase << rechercher sur le web : >>
            if "rechercher sur le web : " in line:

                goodlist = self.petite_recherche(line)

                # TODO : PAS SUR DE l'UTILITE
                super_result, _ = self.ask_to_ai(
                    self.get_client(), goodlist, self.model_to_use
                )

                result_recherche.append(
                    {
                        "resultat_de_recherche": line.split(" : ")[1]
                        + "\n"
                        + super_result
                    }
                )

                bonne_liste = "Recherche sur le Web : \n"
                for recherche in [
                    element["resultat_de_recherche"] for element in result_recherche
                ]:
                    bonne_liste += recherche + "\n\n"

                content += "\nRésultat des recherches : \n" + str(
                    bonne_liste if len(str(recherche)) else ""
                )

            if not isAskToDebride and "en mode débridé" in line:
                isAskToDebride = True

        timing: float = (time.perf_counter_ns() - self.get_timer()) / TIMING_COEF

        return content, isAskToDebride, timing

    def ask_to_ai(self, agent_appel, prompt: str, model_to_use):
        self.set_timer(time.perf_counter_ns())
        letexte, isAskToDebride, timing = self.check_content(content=prompt)
        self.set_timer(time.perf_counter_ns())

        if isinstance(agent_appel, ollama.Client):
            try:
                llm: ollama.Client = agent_appel.chat(
                    model=model_to_use,
                    messages=[
                        {
                            "role": "user",
                            "content": letexte,
                            "num_ctx": 2048,
                            "num_predict": 40,
                            "keep_alive": -1,
                        },
                    ],
                )
                ai_response = llm["message"]["content"]

            except ollama.RequestError as requestError:
                print("OOps aucun model chargé : ", requestError)
            except ollama.ResponseError as responseError:
                print("OOps la requête ne s'est pas bien déroulée", responseError)
        elif isinstance(agent_appel, Groq):

            this_message = [
                {
                    "role": "system",
                    "content": (
                        TODAY_WE_ARE + TEXTE_DEBRIDE
                        if isAskToDebride
                        else (
                            "donne des réponses simples et courtes sauf s'il est stipulé le contraire"
                            + (
                                ("\nYou are an expert in : " + str(self.get_motcles()))
                                if len(self.get_motcles())
                                else ""
                            )
                            + "\n Always use french language, use Markdown format use tags like <code> and </code> or <pre> and </pre> when necessary , and keep conversations alive"
                        )
                    ),
                },
                {
                    "role": "assistant",
                    "content": (
                        # prend tout l'historique des prompts
                        str(self.fenetre_scrollable.get_prompts_history())
                        if len(self.fenetre_scrollable.get_prompts_history())
                        else ""
                    ),
                },
                {
                    "role": "user",
                    "content": letexte,
                },
            ]

            try:
                llm: ChatCompletion = agent_appel.chat.completions.create(
                    messages=this_message,
                    model=model_to_use,
                    temperature=1,
                    max_tokens=4060,
                    n=1,
                    stream=False,
                    stop=None,
                    timeout=10,
                )

                ai_response = llm.choices[0].message.content

            except:
                messagebox.Message("OOps, ")

        elif isinstance(agent_appel, Ola.__class__):
            try:
                llm: Ola = agent_appel(
                    base_url="http://localhost:11434",
                    model=model_to_use,
                    request_timeout=REQUEST_TIMEOUT_DEFAULT,
                    additional_kwargs={
                        "num_ctx": 2048,
                        "num_predict": 40,
                        "keep_alive": -1,
                    },
                )

                ai_response = llm.chat(letexte).message.content

            except:
                messagebox.Message("OOps, ")

        # TODO
        try:
            # calcul le temps écoulé par la thread
            timing: float = (
                timing + (time.perf_counter_ns() - self.get_timer()) / TIMING_COEF
            )
            print(ai_response)
            append_response_to_file(RESUME_WEB, ai_response)
            actualise_index_html(
                texte=ai_response,
                question=letexte,
                timing=timing,
                model=self.get_model(),
            )

            return ai_response, timing
        except:
            print("problème de de délais de réponse")
            return "problème de délais de réponse", timing

    def ask_to_Groq(
        self,
        prompt: str,
        agent_appel=Groq(api_key=GROQ_API_KEY),
        model_to_use=LLAMA370B,
    ):
        """peut s'executer en mode chat_audio"""
        self.set_timer(time.perf_counter_ns())
        letexte, isAskToDebride, timing = self.check_content(content=prompt)
        self.set_timer(time.perf_counter_ns())

        if isinstance(agent_appel, Groq):

            this_message = [
                {
                    "role": "system",
                    "content": (
                        TODAY_WE_ARE + TEXTE_DEBRIDE
                        if isAskToDebride
                        else (
                            "donne des réponses simples et courtes sauf s'il est stipulé le contraire"
                            + (
                                ("\nYou are an expert in : " + str(self.get_motcles()))
                                if len(self.get_motcles())
                                else ""
                            )
                            + "\n Always use french language, use Markdown format use tags like <code> and </code> or <pre> and </pre> when necessary, give only short answers unless clear information is suggested , and keep conversations alive"
                        )
                    ),
                },
                {
                    "role": "assistant",
                    "content": (
                        # prend tout l'historique des prompts
                        str(self.fenetre_scrollable.get_prompts_history())
                        if len(self.fenetre_scrollable.get_prompts_history())
                        else ""
                    ),
                },
                {
                    "role": "user",
                    "content": letexte,
                },
            ]

            try:
                llm: ChatCompletion = agent_appel.chat.completions.create(
                    messages=this_message,
                    model=model_to_use,
                    temperature=1,
                    max_tokens=4060,
                    n=1,
                    stream=False,
                    stop=None,
                    timeout=10,
                )

                ai_response = llm.choices[0].message.content

                timing: float = (
                    time.perf_counter_ns() - self.get_timer()
                ) / TIMING_COEF
                print(ai_response)
                append_response_to_file(RESUME_WEB, ai_response)
                actualise_index_html(
                    texte=ai_response,
                    question=prompt,
                    timing=timing,
                    model=self.get_model(),
                )

                return ai_response, timing

            except:
                messagebox.Message("OOps, ")

        else:
            messagebox.Message("Ne fonctionne qu'avec groq")

        return "pas de réponse", timing

    async def asking(self) -> asyncio.futures.Future:

        if not self.get_client():
            messagebox.showerror(
                title="Client absent",
                message="Vous devez choisir un client, en haut à gauche de l'écran",
            )
            return
        agent_appel = self.get_client()
        response_ai, _timing = self.ask_to_ai(
            agent_appel=agent_appel,
            model_to_use=self.get_model(),
            prompt=self.get_submission(),
        )
        readable_ai_response = response_ai
        self.set_ai_response(readable_ai_response)

        self.fenetre_scrollable.addthing(
            _timing=_timing,
            agent_appel=agent_appel,
            simple_text=self.entree_prompt_principal.get_text(),
            ai_response=response_ai,
            model=self.get_model(),
            submit_func=self.soumettre,
        )

        return readable_ai_response

    def load_txt(self):
        try:
            file_to_read = filedialog.askopenfile(
                parent=self,
                title="Ouvrir un fichier txt",
                defaultextension="txt",
                mode="r",
                initialdir=".",
            )
            print(file_to_read.name)
            resultat_txt = read_text_file(file_to_read.name)
            lire_haute_voix("Fin de l'extraction")

            # on prepare le text pour le présenter à la méthode insert_markdown
            # qui demande un texte fait de lignes séparées par des \n
            # transforme list[str] -> str
            resultat_reformater = "".join(resultat_txt)
            self.entree_prompt_principal.insert_markdown(mkd_text=resultat_reformater)

        except:
            messagebox("Problème avec ce fichier txt")

    def load_and_affiche_txt(self):
        resultat_txt: str = load_txt(self)
        self.entree_prompt_principal.insert_markdown(mkd_text=resultat_txt)

    def load_and_affiche_pdf(self):
        resultat_txt: str = load_pdf(self)
        self.entree_prompt_principal.insert_markdown(mkd_text=resultat_txt)

    def clear_entree_prompt_principal(self):
        self.entree_prompt_principal.replace("1.0", tk.END, "")

    def traite_listbox(self, list_to_check: list) -> tk.Listbox:
        frame = tk.Tk(className="list_ia")
        frame.grid_location(self.winfo_x() + 150, self.winfo_y() + 130)
        _list_box = tk.Listbox(master=frame, width=len(max(list_to_check, key=len)))
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
                prompt_name=str(self.get_motcles()).lower(),
            )
            self.set_submission(preprompt)

            lire_haute_voix("prépromt ajouté : " + preprompt)

        except:
            print("aucun préprompt sélectionné")
            lire_haute_voix("Oups")
        finally:
            w.focus_get().destroy()

    def stoppeur(self):
        lecteur = engine_lecteur_init()
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
        mots_cle = simpledialog.askstring(
            title="YourAssistant - pré-prompts",
            initialvalue="Python",
            prompt="Veuillez entrer le mot-clé à traiter",
        )

        # on set l'attribut motcle de la classe
        self.set_motcles(mots_cle.split())

        # on récupère le tk.Entry de la fenetre principale : frame_of_buttons_principal.motcles_widget
        # on le clean et on y insère le thème récupéré par la simpledialog auparavant
        _speciality_widget: tk.Entry = self.nametowidget(
            "master_frame_actual_prompt.frame_of_buttons_principal.motcles_widget"
        )

        _speciality_widget.select_from(0)
        _speciality_widget.select_to(tk.END)
        _speciality_widget.select_clear()
        _speciality_widget.insert(0, mots_cle)

        # crée et affiche une _listbox remplie avec la variable list_to_check
        _listbox: tk.Listbox = self.traite_listbox(list_to_check)

        # bind sur l'événement sélection d'un item de la liste
        # vers la fonction charge_preprompt
        _listbox.bind("<<ListboxSelect>>", func=self.charge_preprompt)

    def creer_fenetre(self, image: ImageTk, msg_to_write):
        """
        Méthode de création de la fenetre principale"""

        def textwidget_to_mp3(obj: SimpleMarkdownText):
            """
            #### txt vers mp3
            Transforme le text sélectionné dans l'object de type
            SimpleMarkdownText donné en parametre en dictée mp3.
                Si rien n'est sélectionné, tout le text est traité.
            """

            if None == obj.get_selection() or len(obj.get_selection()) == 0:
                # on reécupère tout le contenu de l'objet
                texte_to_save_to_mp3 = obj.get("1.0", tk.END)
            else:
                texte_to_save_to_mp3 = obj.get_selection()

            if len(texte_to_save_to_mp3) > 0:

                lire_haute_voix("transcription du texte vers un fichier mp3")
                simple_dialog = simpledialog.askstring(
                    parent=self,
                    prompt="Enregistrement : veuillez choisir un nom au fichier",
                    title="Enregistrer vers audio",
                )
                engine_lecteur_init().save_to_file(
                    texte_to_save_to_mp3, simple_dialog.lower() + ".mp3"
                )
                lire_haute_voix("terminé")
            else:
                print("rien à transformer")

        def replace_in_place(
            texte: str, index1: str, index2: str, ponctuel: bool = True
        ):
            """traduit sur place (remplacement) le texte sélectionné"""
            self.entree_prompt_principal.replace(
                chars=texte, index1=index1, index2=index2
            )

        def lance_thread_lecture(obj: SimpleMarkdownText):
            try:
                texte_to_talk = obj.get(tk.SEL_FIRST, tk.SEL_LAST)
            except:
                texte_to_talk = obj.get("1.0", tk.END)
            finally:
                lire_haute_voix(texte_to_talk)

        def translate_inplace():
            traduit_maintenant()

        def traduit_maintenant():
            self.set_timer(float(time.perf_counter_ns()))
            was_a_list = False
            try:
                # TRANSLATE IN PLACE
                texte_initial = self.entree_prompt_principal.get_selection()
                indx1 = self.entree_prompt_principal.index(tk.SEL_FIRST)
                indx2 = self.entree_prompt_principal.index(tk.SEL_LAST)

                texte_traite = traitement_du_texte(texte_initial, 500)
                if isinstance(texte_traite, list):
                    for element in texte_traite:
                        translated_text = str(translate_it(text_to_translate=element))
                        replace_in_place(
                            texte=translated_text,
                            index1=indx1,
                            index2=indx2,
                            ponctuel=False,
                        )
                else:
                    translated_text = str(translate_it(text_to_translate=texte_traite))
                    replace_in_place(
                        texte=translated_text, index1=indx1, index2=indx2, ponctuel=True
                    )

            except:
                # TRANSLATE COMPLETE
                texte_initial = self.entree_prompt_principal.get("1.0", tk.END)
                texte_brut_initial = texte_initial.replace("\n", " ")
                texte_traite = traitement_du_texte(texte_initial, 500)

                if isinstance(texte_traite, list):
                    sortie = ""
                    for element in texte_traite:
                        translated_text = str(translate_it(text_to_translate=element))
                        sortie += "\n" + translated_text
                    was_a_list = True

                    timing: float = (
                        time.perf_counter_ns() - self.get_timer()
                    ) / TIMING_COEF
                    self.fenetre_scrollable.addthing(
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
                    self.fenetre_scrollable.addthing(
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
                    self.fenetre_scrollable.addthing(
                        _timing=timing,
                        agent_appel=self.get_client(),
                        simple_text=self.entree_prompt_principal.get_text(),
                        ai_response=translated_text,
                        model=self.get_model(),
                        submit_func=self.soumettre,
                    )

                lire_haute_voix("fin de la traduction")

        # préparation de l'espace de saisie des prompts

        self.affiche_ban()
        self.master_frame_actual_prompt = tk.Canvas(
            self, relief="sunken", name="master_frame_actual_prompt"
        )
        self.master_frame_actual_prompt.pack(side=tk.BOTTOM, fill="both", expand=False)
        self.frame_of_buttons_principal = tk.Frame(
            self.master_frame_actual_prompt,
            relief="sunken",
            name="frame_of_buttons_principal",
        )
        self.frame_of_buttons_principal.configure(
            background=from_rgb_to_tkColors(DARK3), width=10
        )
        self.frame_of_buttons_principal.pack(fill="x", expand=True)

        self.frame_actual_prompt = tk.Frame(
            self.master_frame_actual_prompt, relief="sunken"
        )
        self.frame_actual_prompt.pack(side=tk.BOTTOM)

        self.default_font = tkfont.nametofont("TkDefaultFont")
        self.default_font.configure(size=8)

        self.entree_prompt_principal = SimpleMarkdownText(
            self.frame_actual_prompt, height=15, font=self.default_font
        )
        self.entree_prompt_principal.widgetName = "entree_prompt_principal"

        # Attention la taille de la police, ici 10, ce parametre
        # tant à changer le cadre d'ouverture de la fenetre
        self.entree_prompt_principal.configure(
            bg=from_rgb_to_tkColors(LIGHT0),
            fg=from_rgb_to_tkColors(DARK3),
            font=("Arial", 12),
            wrap="word",
            padx=10,
            pady=6,
        )
        self.boutton_effacer_entree_prompt_principal = tk.Button(
            self.frame_of_buttons_principal,
            text="x",
            command=self.clear_entree_prompt_principal,
        )
        self.boutton_historique = tk.Button(
            self.frame_of_buttons_principal,
            text="historique",
            command=lambda: self.affiche_histoy(
                [
                    element["response"]
                    for element in self.fenetre_scrollable.get_prompts_history()
                ]
            ),
        )
        self.boutton_effacer_entree_prompt_principal.configure(
            bg="red", fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.boutton_effacer_entree_prompt_principal.pack(side="right")
        self.boutton_historique.pack(side="right")
        self.scrollbar_prompt_principal = tk.Scrollbar(self.frame_actual_prompt)
        self.scrollbar_prompt_principal.pack(side=tk.RIGHT, fill="both")
        self.entree_prompt_principal.tag_configure(
            "italic", font=str(self.entree_prompt_principal.cget("font") + " italic")
        )
        self.entree_prompt_principal.insert_markdown(
            mkd_text=msg_to_write + " **< CTRL + RETURN > pour valider.**"
        )
        self.entree_prompt_principal.focus_set()
        self.entree_prompt_principal.pack(side=tk.BOTTOM)
        self.entree_prompt_principal.configure(
            yscrollcommand=self.scrollbar_prompt_principal.set
        )
        self.entree_prompt_principal.bind("<Control-Return>", func=self.go_submit)

        # Création d'un champ de saisie de l'utilisateur
        self.scrollbar_prompt_principal.configure(
            command=self.entree_prompt_principal.yview, bg=from_rgb_to_tkColors(DARK2)
        )

        self.bouton_stop = tk.Button(
            self.frame_of_buttons_principal, text="Stop", command=self.stoppeur
        )
        self.bouton_stop.configure(bg="red", fg="white")
        # self.bouton_stop.pack(side=tk.LEFT)

        # Création d'un bouton pour Lire
        self.bouton_lire1 = tk.Button(
            self.frame_of_buttons_principal,
            text="Lire",
            command=lambda: lance_thread_lecture(self.entree_prompt_principal),
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
            self.frame_of_buttons_principal, text="Traduire", command=translate_inplace
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
            self.frame_of_buttons_principal,
            text=" ф ",
            command=self.lance_thread_ecoute,
        )
        self.bouton_commencer_diction.configure(
            bg="red", fg=from_rgb_to_tkColors(LIGHT3), width=10
        )

        self.bouton_commencer_diction.pack(side=tk.LEFT)

        # Création d'un bouton pour soumetre
        self.bouton_soumetre = tk.Button(
            self.frame_of_buttons_principal, text="Ask to AI", command=self.soumettre
        )
        self.bouton_soumetre.configure(
            bg=from_rgb_to_tkColors((120, 120, 120)),
            fg=from_rgb_to_tkColors(LIGHT3),
            highlightbackground="red",
            highlightcolor=from_rgb_to_tkColors(LIGHT3),
        )
        self.bouton_soumetre.pack(side=tk.LEFT)

        self.bouton_save_to_mp3 = tk.Button(
            self.frame_of_buttons_principal,
            text="texte vers mp3",
            command=lambda: textwidget_to_mp3(self.entree_prompt_principal),
        )
        self.bouton_save_to_mp3.configure(
            bg=from_rgb_to_tkColors(DARK1), fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.bouton_save_to_mp3.pack(side="left")

        self.bouton_load_pdf = tk.Button(
            self.frame_of_buttons_principal,
            text="Charger Pdf",
            command=self.load_and_affiche_pdf,
        )
        self.bouton_load_pdf.configure(
            bg=from_rgb_to_tkColors(DARK2), fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.bouton_load_pdf.pack(side="left")

        self.bouton_load_txt = tk.Button(
            self.frame_of_buttons_principal,
            text="Charger TXT",
            command=self.load_and_affiche_txt,
        )
        self.bouton_load_txt.configure(
            bg=from_rgb_to_tkColors(DARK3), fg=from_rgb_to_tkColors((255, 255, 255))
        )
        self.bouton_load_txt.pack(side="left")

        self.motcles_widget = tk.Entry(
            self.frame_of_buttons_principal,
            name="motcles_widget",
            width=30,
            fg="red",
            bg=from_rgb_to_tkColors(DARK3),
            font=("trebuchet", 10, "bold"),
            relief="flat",
        )
        self.button_keywords = tk.Button(
            self.frame_of_buttons_principal,
            text="Mot-clé",
            background=from_rgb_to_tkColors(DARK2),
            foreground=from_rgb_to_tkColors(LIGHT3),
            command=lambda: self.affiche_prepromts(PROMPTS_SYSTEMIQUES.keys()),
        )
        self.button_keywords.pack(side=tk.RIGHT, expand=False)
        self.motcles_widget.pack(side="left", padx=2, pady=2)

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
            w.focus_get().destroy()

    def demander_actu(self, evt: tk.Event):

        # Note here that Tkinter passes an event object to onselect()
        w: tk.Listbox = evt.widget
        try:
            index = w.curselection()[0]
            value = w.get(index)
            print('You selected item %d: "%s"' % (index, value))
            content_selected = [
                item["content"] for item in RULS_RSS if item["title"] == value
            ].pop()

            if "le monde informatique" in value.lower():
                feed_rss = my_feedparser_rss.le_monde_informatique(
                    content_selected.split(" | ")
                )
            elif "global_search" in value.lower():
                feed_rss = my_feedparser_rss.generic_search_rss(
                    rss_url=content_selected.split(" | "), nombre_items=10
                )
            else:
                feed_rss = my_feedparser_rss.lemonde(content_selected.split(" | "))

            response = self.envoyer_audio_prompt(
                content_discussion=make_resume(feed_rss),
                necessite_ai=False,
                grorOrNot=False,
            )

            self.set_submission(response)

        except Exception as e:
            lire_haute_voix("Aïe !! demande d'actualité : ", e)

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

    def affiche_histoy(self, list_to_check: list):
        """
        Display a list of AI you can use
        * affiche la listebox avec la liste donnée en paramètre list_to_check
        * click on it cause model AI to change
        """
        _listbox: tk.Listbox = self.traite_listbox(list_to_check)
        _listbox.configure(width=200)
