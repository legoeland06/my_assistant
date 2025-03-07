from asyncio.log import logger
from datetime import datetime

import json
import random
import time
from tkinter import ALL, filedialog, messagebox, simpledialog
from typing import Any, Tuple
from groq import Groq
import ollama
from openai import ChatCompletion, OpenAI  # type: ignore
import pyaudio
from Article import Article
from Constants import (
    LLAMA3,
    CATEGORY_SEPARATOR,
    ZEFONT,
    LLAMA370B,
    DARK2,
    DARK3,
    RULS_RSS,
    BANNIERE_HEIGHT,
    LIGHT0,
    ANNULE,
    LIGHT3,
    URL_ACTU_GLOBAL_RSS,
    C_NOTE,
    MAX_HISTORY,
    CLICK_LIST,
    LIST_COMMANDS,
    LIGHT2,
    DARK1,
    RESPONSE,
    TIMING_COEF,
    YOU_SELECT_VALUE,
)
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
    about_this_book,
    attentif,
    get_stream,
    lire_text_from_object,
    loadimage,
    question_oui_non,
    recup_infos_rss_feed,
    reformat_text,
    threads_outils,
    append_saved_texte,
    ask_to_ai,
    ask_to_resume,
    charge_image,
    downloadimage,
    get_news_api,
    create_asyncio_task,
    lancer_chrome,
    lancer_search_chrome,
    lecteur_init,
    from_rgb_to_tkcolors,
    get_groq_ia_list,
    get_pre_prompt,
    get_engine,
    letters_to_number,
    lire,
    load_pdf,
    load_txt,
    make_resume,
    question_oui_non_annule,
    question_ouverte,
    read_text_file,
    tester_appelation,
    traitement_du_texte,
    translate_it,
)
import secret

type History = list[Conversation]


class FenetrePrincipale(tk.Frame):

    def __init__(
        self,
        title: str,
        # model ia à utiliser
        model_to_use: str,
        master,
    ):
        super().__init__(master)
        self.master = master
        self.pseudo = "kiki"
        self.ia = LLAMA3
        self.debride = False
        self.history = []
        self.calice = []
        self.searchHystory = []
        self.title = title
        self.ai_response = str()
        self.nb_mots = 4
        self.thread = None
        self.threads = []
        self.valide = True
        self.ok_to_Read = True
        self.prompts_history = []
        self.responses = []
        self.submission = str()
        self.set_mode_prompt_off()
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
            Image.open("images/banniere.png").reduce(2)
        )  # type: ignore
        self.image_button_diction1 = charge_image("images/oeil1.jpg", 200)
        self.image_button_diction2 = charge_image("images/oeil2.jpg", 200)
        self.image_button_diction3 = charge_image("images/oeil3.jpg", 200)

        self.image_link = str()
        self.content = str()
        self.widgetMotcles: tk.Entry | None = None

        # phase de construction de la fenetre principale
        self.creer_fenetre(
            msg_to_write="Prompt...",
        )
        self.my_liste = []
        self.messages = [
            {
                "role": "user",
                "content": "Bonjour",
            },
        ]
        self.actual_chat_completion = []
        self.engine_model = get_engine()
        self.streaming = get_stream()
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

    def set_pseudo(self, pseudo: str):
        self.pseudo = pseudo

    def get_pseudo(self) -> str:
        return self.pseudo

    def bypass(self):
        """by pass les sélections dIa et de client"""
        deepseek_client=OpenAI(api_key=secret.DEEPSEEK_API, base_url="https://api.deepseek.com")
        self.set_client(deepseek_client)
        self.set_model("deepseek-chat")
        self.lance_thread_ecoute()

    def set_debride(self, status: bool):
        self.debride = status

    def get_debride(self) -> bool:
        return self.debride

    def set_ok_to_Read(self, ok_to_read: bool):
        """setter for chatAudioMode"""
        self.ok_to_Read = ok_to_read

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

    def set_thread(self, thread: StoppableThread | None):
        self.thread = thread
        if thread is None:
            try:
                threads_outils.remove(thread)
                lire("thread supprimée de la liste des threads")
            except Exception as e:
                print(f"aucune thread à supprimer : {e}")

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
        lire("changement du client : " + str(type(self.client)))

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

    def get_mode_prompt(self):
        """
        ## ce booléen spécifie si les mots enregistrés du microphones
        * FALSE sont une commandes vocale elle doit etre effacée du prompt
        * TRUE sont un prompt et doivent être maintenues inchangées (initialisée comme telle par defaut)
        """
        return self.mode_prompt

    def set_mode_prompt_off(self):
        """
        ## ce booléen spécifie si les mots enregistrés du microphones
        * FALSE sont une commandes vocale elle doit etre effacée du prompt
        * TRUE sont un prompt et doivent être maintenues inchangées (initialisée comme telle par defaut)
        """
        self.mode_prompt = False
        return self.mode_prompt

    def set_mode_prompt_on(self):
        """
        ## ce booléen spécifie si les mots enregistrés du microphones
        * FALSE sont une commandes vocale elle doit etre effacée du prompt
        * TRUE sont un prompt et doivent être maintenues inchangées (initialisée comme telle par defaut)
        """
        self.mode_prompt = True
        return self.mode_prompt

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
        return True if lire("changement d'ia: " + self.model_to_use) else False

    def get_model(self) -> str:
        return self.model_to_use

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
            self, background=from_rgb_to_tkcolors(DARK2), name="cnvs1"
        )
        # self.canvas_principal_banniere.configure(height=BANNIERE_HEIGHT/2)
        self.canvas_principal_banniere.pack(fill="x", expand=True)
        # ################################
        self.canvas_buttons_banniere = tk.Frame(
            self.canvas_principal_banniere, name="cnvs2"
        )
        self.canvas_buttons_banniere.configure(bg=from_rgb_to_tkcolors(DARK3))
        self.canvas_buttons_banniere.pack(fill="x", expand=False)

        # Create a canvas
        self.canvas_image_banniere = tk.Canvas(
            self.canvas_principal_banniere,
            height=BANNIERE_HEIGHT,
            background=from_rgb_to_tkcolors(DARK2),
            name="canva",
        )

        # Création d'un bouton pour quitter
        self.bouton_quitter = tk.Button(
            self.canvas_buttons_banniere,
            font=self.btn_font,
            relief="flat",
            text="📴",
            border=0,
            command=self.ask_before_quit,
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

        self.bouton_liste_actu = tk.Button(
            self.canvas_buttons_banniere,
            font=self.btn_font,
            text="Liste Actu",
            command=lambda: self.call_display_listbox_actu(
                [
                    f"{item['title']} :: {item['content'].replace(CATEGORY_SEPARATOR,", ")}"
                    for item in RULS_RSS
                ],
                mode_audio=False,
            ),
            relief="flat",
            highlightthickness=3,
            highlightcolor="yellow",
            activeforeground="white",
        )
        self.bouton_liste_actu.configure(foreground="red", background="black")

        # await self.recup_debriderbouton_activeACTU

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
        self.bouton_liste_actu.pack(side=tk.LEFT)

        self.label_slogan = tk.Label(
            self.canvas_buttons_banniere,
            text=slogan,
            font=("Trebuchet Bold Italic", 8),
            bg="black",
            border=0,
            relief="flat",
            fg=from_rgb_to_tkcolors(LIGHT3),
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
        _ = self.entree_prompt_principal.get_text()
        if _.__len__():
            self.set_submission(_)
        else:
            return False
        return True

    def debride_switch(self, status):
        self.set_debride(status=status)
        if self.get_debride():
            self.bouton_desactive_debride.pack(side=tk.LEFT)
            self.bouton_active_debride.pack_forget()
        else:
            self.bouton_active_debride.pack(side=tk.LEFT)
            self.bouton_desactive_debride.pack_forget()

    def ask_before_quit(self):
        # Afficher une boîte de message de confirmation
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir quitter ?"):
            self.quitter()
        else:
            print("L'utilisateur a annulé.")

    def quitter(self):
        get_stream().close()
        lire("au revoir !")
        self.delete_all_threads()
        time.sleep(2)
        self.master.destroy()
        time.sleep(2)
        self.quit()
        time.sleep(2)
        exit(0)

    def delete_all_threads(self):
        self.save_to_submission()
        mainthread = threading.main_thread()
        for i in threading.enumerate():
            if i != mainthread:
                print(f"ThreadThreading::{i.getName()}")
                i.stop()  # type: ignore

        for j in self.threads:
            if isinstance(j, StoppableThread):
                print(f"ThreadThreads::{j.getName()}")
                j.stop()

        for t in threads_outils:
            print(f"ThreadThreading::{t.getName()}")
            t.stop() if isinstance(t, StoppableThread) else None

        for element in threading.enumerate():
            print(f"threading_enumerated {element}")

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
            lire("un instant s'il vous plait")
            _nb_chars = len(self.get_submission())
            print("nombre de charactères:: " + str(_nb_chars))
            if _nb_chars >= 3000:
                new_prompt_list = _traitement_du_texte(self.get_submission(), 200)
                lire(
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
        if (
            self.get_thread() is not None
            and self.get_thread().getName() == "mode_veille"
        ):
            return None

        self.bouton_commencer_diction.configure(
            image=self.image_button_diction2,  # type: ignore
        )
        self.bouton_commencer_diction.update()

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

        # self.get_thread().join()

    def get_synonymsOf(self, expression):
        prompt = (
            "en français exclusivement et sous la forme d'une liste non numérotée, donne 20 façons différentes de dire : ("
            + expression
            + ") dans le contexte d'un échange verbal, en réponse je ne veux rien d'autre que le résultat du type: phrase_1\nphrase_2\nphrase_3\netc...]"
        )
        _ = self.get_client()
        if isinstance(_, Groq):
            try:
                llm: ChatCompletion = _.chat.completions.create(
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
            except Exception as e:
                messagebox.Message(f"{e}")
                return expression
            ai_response_list = str(ai_response).split("\n")
            return ai_response_list[
                (round(random.randint(1, 19 * 10) / 10) % (len(ai_response_list) - 1))
                + 1
            ]
        return expression

    def reformule(self, expression):
        prompt = "Trouve moi une autre formulation de cette expression: " + expression
        _ = self.get_client()
        if isinstance(_, Groq):
            try:
                llm: ChatCompletion = _.chat.completions.create(
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
            except Exception as e:
                messagebox.Message(f"{e}")
                return expression
            ai_response_ = str(ai_response)
            return ai_response_
        return expression

    async def dialog_ia(self):
        _content: str = str()
        self.open_microphone()
        lire(
            "Bienvenue ! pour activer les commandes vocales, il suffit de dire : << passe en mode audio >>"
        )

        # entrez dans le mode veille
        if get_stream().is_stopped():
            get_stream().start_stream()

        _content = _content + await self.mode_veille()

        print("Sortie de mode interactif")

        return True

    async def mode_veille(self):
        content_commandes_vocales = str()
        self.set_mode_prompt_off()
        while True:
            if get_stream().is_stopped():
                get_stream().start_stream()

            check_ecoute: str = attentif()
            print("\n" + "*" * 40 + "\n" + "==> " + check_ecoute + "\n" + "*" * 40 + "\n")

            if await self.handle_check_ecoute(check_ecoute, content_commandes_vocales):
                break

            if self.get_mode_prompt():
                content_commandes_vocales += " " + check_ecoute

        return content_commandes_vocales

    async def handle_check_ecoute(self, check_ecoute, content_commandes_vocales):
        if "afficher de l'aide" in check_ecoute:
            _ = self.display_help()
        elif "quel est le mode actuel" in check_ecoute:
            self.witch_mode("veille")
        elif any(keyword in check_ecoute for keyword in ["fermer", "ferme"]):
            if "l'application" in check_ecoute:
                await self.close_application(content_commandes_vocales)
                return True
        elif any(keyword in check_ecoute for keyword in ["active", "passe"]):
            await self.handle_active_commands(check_ecoute, content_commandes_vocales)
        return False

    async def close_application(self, content_commandes_vocales):
        get_stream().stop_stream()
        self.bouton_commencer_diction.configure(image=self.image_button_diction1)  # type: ignore
        self.entree_prompt_principal.configure(bg=from_rgb_to_tkcolors(LIGHT0))
        self.bouton_commencer_diction.update()
        append_saved_texte(file_to_append="saved_text", readable_ai_response=content_commandes_vocales)
        lire("ok, vous pouvez réactiver l'observeur audio en appuyant sur le bouton casque")
        self.set_thread(None)

    async def handle_active_commands(self, check_ecoute, content_commandes_vocales):
        if any(keyword in check_ecoute for keyword in ["mode audio", "commandes vocales"]):
            await self.activate_audio_mode(content_commandes_vocales)
        elif "mode débridé" in check_ecoute:
            self.debride_switch(True)
            lire("mode débridé activé")
        elif "mode normal" in check_ecoute:
            self.debride_switch(False)
            lire("mode debridé désactivé")

    async def activate_audio_mode(self, content_commandes_vocales):
        get_stream().stop_stream()
        self.bouton_commencer_diction.configure(image=self.image_button_diction3)  # type: ignore
        self.entree_prompt_principal.configure(bg=from_rgb_to_tkcolors((DARK3)), fg=from_rgb_to_tkcolors((182, 78, 20)))
        self.bouton_commencer_diction.update()
        lire("pour sortir, dites : fin de la session")
        get_stream().start_stream()
        self.open_microphone()
        content_commandes_vocales += " " + await self.mode_commandes_vocales()

    async def mode_commandes_vocales(self):
        multi_line = str()
        self.setup_vocal_mode_ui()
        while not self.micro_is_cut:
            self.set_mode_prompt_on()
            ck_ecoute: str = attentif()
            print(f"\n{'*' * 40}\n==> {multi_line}\n{ck_ecoute}\n{'*' * 40}\n")
            await self.process_vocal_commands(ck_ecoute, multi_line)
        return multi_line

    def setup_vocal_mode_ui(self):
        self.button_quit_mode_vocal = tk.Button(
            master=self.canvas_diction,
            text="MODE VEILLE",
            command=self.cut_microphone,
            background=from_rgb_to_tkcolors(DARK3),
            foreground=from_rgb_to_tkcolors(LIGHT3),
        )
        self.button_quit_mode_vocal.pack(side=tk.BOTTOM, fill="x", expand=True)

    async def process_vocal_commands(self, ck_ecoute, multi_line):
        if "afficher" in ck_ecoute and any(keyword in ck_ecoute for keyword in ["de l'aide", "les commandes"]):
            await self.handle_help_command()
        elif "quel est le mode actuel" in ck_ecoute:
            self.witch_mode("commandes vocales")
        elif "quel jour sommes-nous" in ck_ecoute:
            await self.handle_date_command()
        elif "quelle heure est-il" in ck_ecoute:
            await self.handle_time_command()
        elif "est-ce que tu m'écoutes" in ck_ecoute:
            await self.handle_listening_command()
        elif "lancer une application" in ck_ecoute:
            self.lancer_application(ck_ecoute)
        elif any(keyword in ck_ecoute for keyword in ["effacer", "supprimer"]) and any(keyword in ck_ecoute for keyword in ["conversation", "discussion"]):
            self.effacer_discussion(ck_ecoute)
        elif any(keyword in ck_ecoute for keyword in ["conversation", "discussion"]):
            self.afficher_conversations(ck_ecoute)
        elif any(keyword in ck_ecoute for keyword in ["les actualités", "les informations"]) and "affiche" in ck_ecoute:
            await self.affiche_actualites(ck_ecoute)
        elif " propos d'un livre" in ck_ecoute:
            await self.handle_book_command()
        elif "donne-moi les infos" in ck_ecoute:
            await self.get_informations()
        elif "faire une recherche web sur " in ck_ecoute:
            ck_ecoute = await self.recherche_web(ck_ecoute)
        elif any(keyword in ck_ecoute for keyword in ["fin de", "ferme", "termine"]) and "la session" in ck_ecoute:
            await self.handle_end_session_command(multi_line, ck_ecoute)
        elif "lis-moi systématiquement tes réponses" in ck_ecoute:
            self.set_ok_to_Read(True)
            lire(C_NOTE)
        elif "arrêtez la lecture systématique des réponses" in ck_ecoute:
            self.set_ok_to_Read(False)
            lire(C_NOTE)
        elif "gérer les préférences" in ck_ecoute:
            self.gerer_prefs()
        elif "la validation orale" in ck_ecoute:
            await self.handle_validation_command(ck_ecoute)
        if self.get_mode_prompt() and len(ck_ecoute.split()) >= self.nb_mots:
            multi_line = await self.valider_prompt(multi_line, ck_ecoute)
        try:
            get_stream().start_stream()
        except NameError as nerr:
            print(nerr)

    async def handle_help_command(self):
        self.set_mode_prompt_off()
        _ = self.display_help()
        lire("état des lieux de la configuration du tchat intéractif")
        lire("je vous lis systématiquement les réponses" if self.get_ok_to_Read() else "les réponses ne sont pas lues")
        lire("à la fin de votre question ou prompt valide, je vous demande si vous avez terminé" if self.getValide() else "dès lors que votre prompte est valide, je déclenche ma réponse.")
        lire(f"un prompt est valide dès lors qu'il contient au moins {str(self.nb_mots)} mots")

    async def handle_date_command(self):
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        lire(self.get_synonymsOf("Nous sommes le " + time.strftime("%Y-%m-%d")))

    async def handle_time_command(self):
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        lire(self.get_synonymsOf("il est exactement " + time.strftime("%H:%M:%S", time.localtime())))

    async def handle_listening_command(self):
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        lire(self.get_synonymsOf(f"oui je suis toujours à l'écoute {self.get_pseudo()}"))

    async def handle_book_command(self):
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        lire("choisissez votre texte d'investigation")
        book = load_txt(None)
        question = question_ouverte("quelle est votre question ?")
        print(f"Question:{question}")
        _response, _timer = await about_this_book(book, question)
        lire(_response)

    async def handle_end_session_command(self, multi_line, ck_ecoute):
        get_stream().stop_stream()
        self.cut_microphone()
        return multi_line + " " + ck_ecoute

    async def handle_validation_command(self, ck_ecoute):
        if any(keyword in ck_ecoute for keyword in ["active", "activer", "activez"]):
            get_stream().stop_stream()
            self.set_mode_prompt_off()
            self.setValide(True)
            lire(C_NOTE)
        elif any(keyword in ck_ecoute for keyword in ["stopper", "arrêter", "arrêtez"]):
            get_stream().stop_stream()
            self.set_mode_prompt_off()
            self.setValide(False)
            lire(C_NOTE)

    async def valider_prompt(self, multi_line, ck_ecoute):
        get_stream().stop_stream()

        if self.getValide():
            result = question_oui_non_annule(
                        "avez vous terminé ?",
                    )

            if ANNULE == result:
                get_engine().Reset()
                lire("ok, j'efface votre phrase précédente")

            elif result:
                _response = await self.send_prompt(
                            multi_line + "\n" + ck_ecoute,
                            necessite_ai=True,
                            needed_groq=True,
                        )
                await self.check_before_read(_response)
                multi_line = str()

            elif not result:
                multi_line += "\n" + ck_ecoute

                lire("continuez")

            del result

        else:
            _response = await self.send_prompt(
                        ck_ecoute, necessite_ai=True, needed_groq=True
                    )

            await self.check_before_read(_response)
        return multi_line

    def gerer_prefs(self):
        nbmot: int | bool = letters_to_number(
                    question_ouverte(
                        "à partir de combien de mots dois je déclencher ma réponse ?",
                    )
                )
        if not nbmot:
            self.nb_mots = 4
        elif isinstance(nbmot, int):
            self.nb_mots = nbmot

        self.set_pseudo(question_ouverte("Quel est votre pseudo ?"))
        lire("merci")

        _question_validation = question_oui_non(
                    "souhaitez vous une validation orale de vos prompt ?",
                )
        _question_ok_to_read = question_oui_non(
                    "souhaitez vous une réponse orale de vos prompt ?",
                )
        self.setValide(valide=True if _question_validation else False)
        self.set_ok_to_Read(ok_to_read=True if _question_ok_to_read else False)

        self.set_mode_prompt_off()
        lire(
                    f"c'est noté  {self.pseudo}: je récupère les prompts à partir de {str(self.nb_mots)} mots \
                     {"et je demande validation" if _question_validation else str() } avant de vous {"lire" if _question_ok_to_read else "afficher"} ma réponse."
                )

    async def recherche_web(self, ck_ecoute):
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        ck_ecoute = ck_ecoute.replace(
                    " faire une recherche web sur", "\nrechercher sur le web : "
                )

        _websearching = await self.send_prompt(
                    ck_ecoute, necessite_ai=True, needed_groq=False
                )
        await self.check_before_read(_websearching)
        return ck_ecoute

    async def get_informations(self):
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        _motcle, articles = await self.recup_informations(
                    letters_to_number(
                        question_ouverte(
                            "combien d'articles souhaitez vous que je tente de récupèrer ?",
                        )
                    )
                )
        if (
                    question_oui_non(
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
                lire(
                            translate_it(
                                article.title
                                + " "
                                + article.description
                                + " "
                                + article.content
                            )
                        )

    async def affiche_actualites(self, ck_ecoute):
        get_stream().stop_stream()

        if "toutes" in ck_ecoute:
            self.get_all_news()
        elif "africaines" in ck_ecoute:
            self.get_all_africa_news()
        else:
            final_list = [
                        f"{n}. {item['title']} :: {item['content'].replace(CATEGORY_SEPARATOR,", ")}"
                        for n, item in enumerate(RULS_RSS)
                    ]
            _c, _t = await self.display_listbox_actus(
                        final_list, mode_audio=True
                    )

        self.set_mode_prompt_off()

    def afficher_conversations(self, ck_ecoute):
        if any(
                    keyword in ck_ecoute for keyword in ["la liste des", "historique"]
                ):
            self.affiche_liste()

        elif "la dernière" in ck_ecoute:
            self.affiche_derniere(ck_ecoute)

        elif "une" in ck_ecoute:
            self.affiche_une(ck_ecoute)

    def affiche_liste(self):
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        lire("Voici")
        self.display_history()

    def affiche_derniere(self, ck_ecoute):
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        _discussion: Conversation
        _conversation = self.responses[len(self.responses) - 1]
        _last_discussion: Conversation = self.nametowidget(_conversation)

        if "affiche" in ck_ecoute:
            _last_discussion.affiche_fenetre_agrandie()
        if "archive" in ck_ecoute:
            _last_discussion.create_pdf()
        elif any(
                        keyword in ck_ecoute for keyword in ["lis-moi", "lis moi"]
                    ):
            lire(
                            f"Contenu de la dernière conversation sur un total de {self.responses.__len__()} conversations enregistrées. "
                            + _last_discussion.get_ai_response()
                        )

    def affiche_une(self, ck_ecoute):
        zenumber: int = letters_to_number(
                        question_ouverte(
                            "laquelle ?",
                        )
                    )
        nb_conversations = len(self.responses)
        if zenumber <= nb_conversations:
            _conversation = self.responses[zenumber - 1]
            _discussion: Conversation = self.nametowidget(_conversation)
            _last_discussion: Conversation = self.nametowidget(_conversation)
            if "affiche" in ck_ecoute:
                _discussion.affiche_fenetre_agrandie()
            elif "archive" in ck_ecoute:
                _discussion.create_pdf()
            elif any(
                            keyword in ck_ecoute
                            for keyword in ["lis-moi", "lis moi", "dis-moi", "dis moi"]
                        ):
                _last_discussion.lire()
            self.set_mode_prompt_off()

        else:
            self.set_mode_prompt_off()
            lire(
                            "je suis désolé mais il n'y a pas plus de "
                            + str(nb_conversations)
                            + " conversations en mémoire"
                        )

    def effacer_discussion(self, ck_ecoute):
        if "historique" in ck_ecoute:
            get_stream().stop_stream()
            self.set_mode_prompt_off()
            self.delete_history()

        elif "la dernière" in ck_ecoute:
            get_stream().stop_stream()
            self.set_mode_prompt_off()
            self.delete_last_discussion()

        elif "les dernières" in ck_ecoute:
            get_stream().stop_stream()
            self.set_mode_prompt_off()
            for _ in range(letters_to_number(question_ouverte("combien ?"))):
                self.delete_last_discussion()

    def lancer_application(self, ck_ecoute):
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        if any(keyw in ck_ecoute for keyw in ["internet", "chrome", "google"]):
            lancer_search_chrome(
                        question_ouverte(
                            "Que voulez vous chercher ?",
                        ).replace(" ", "+")
                    )
        else:
            lancer_chrome(
                        tester_appelation(
                            question_ouverte(
                                "laquelle ?",
                            )
                        )
                        or str()
                    )

    def witch_mode(self, mode: str):
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        lire(f"nous sommes actuellement dans le mode {mode}")

    def cut_microphone(self):
        self.micro_is_cut = True
        self.button_quit_mode_vocal.destroy()
        self.command_quit_session()

    def open_microphone(self):
        self.micro_is_cut = False

    def command_quit_session(self):
        self.entree_prompt_principal.configure(
            bg=from_rgb_to_tkcolors(LIGHT0), fg=from_rgb_to_tkcolors(DARK3)
        )
        self.set_mode_prompt_off()

        self.bouton_commencer_diction.configure(
            image=self.image_button_diction2,  # type: ignore
        )
        self.bouton_commencer_diction.update()

        lire("merci. Pour ré-activer le mode commande vocales, il s'uffit de demander")
        time.sleep(1)

    def about_africa(self):
        rubrique = []
        feeds = [
            "https://www.africanews.com/feed/rss?themes=news,"
            "https://feeds.feedburner.com/AfricaIntelligence",
            "https://feeds.feedburner.com/LaLettre-fr",
            "https://feeds.feedburner.com/IntelligenceOnline/",
        ]
        for item in feeds:
            resultat = str()
            feed = my_feedparser_rss.feedparser.parse(item)

            for entry in feed.entries:
                resultat += translate_it(str(entry.title)) + "\n"
                resultat += translate_it(str(entry.description)) + "\n"

            print("\n" + "*" * 40 + "\n" + resultat + "\n" + "*" * 40)
            rubrique.append(resultat)

        return rubrique

    def get_all_africa_news(self):
        self.calice = []
        lire("récupérations des actualités africaines en cours...")
        self.set_mode_prompt_off()
        recup = self.about_africa()
        print(f"longueur du resultat : {recup.__len__()}")
        print(recup[0])
       
    def get_all_news(self):
        self.calice = []
        for liste_rss in URL_ACTU_GLOBAL_RSS:
            lire(
                "\nSujet: "
                + liste_rss["title"]
                + "\nRubriques: "
                + liste_rss["content"].replace(CATEGORY_SEPARATOR, ", ")
            )

            lire("récupérations des actualités globales en cours...")

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
                feed_rss = my_feedparser_rss.lemonde(liste_rss["content"].split(" | "))

            self.set_mode_prompt_off()
            for category in map(translate_it, feed_rss):
                if category.__len__():
                    _response = self.send_prompt(
                        content_discussion=make_resume(category),
                        necessite_ai=True,
                        needed_groq=False,
                    )
                    self.calice.append(_response)
                    # lire(_response)
                    time.sleep(4)
        self.display_search_list_results(self.calice)

    def display_search_list_results(self, calice: list):
        if calice == []:
            return
        if question_oui_non(
            f"nous avons archivé {calice.__len__()} news, voulez-vous que je vous les présente"
        ):

            def lire_calice_news(evt: tk.Event):
                w: tk.Listbox = evt.widget
                idx = w.curselection()
                print(f"idx={str(idx)}")
                index = idx[0]
                value: str = w.get(index)

                print('You selected item : "%s"' % value)

                lire(calice[index])

            _list = [f"{n}:: {element}" for n, element in enumerate(calice)]
            _list_good = [
                f"{n}:: {str(" ").join(element.split(":: ")[1].split()[:5])}"
                for n, element in enumerate(_list)
            ]
            _listbox = self.traite_listbox(_list_good, "actu_news")
            _listbox.bind(CLICK_LIST, func=lire_calice_news)
            _list_good.append(ANNULE)
            ze_choix = letters_to_number(
                question_ouverte("faites votre choix : ", _list_good)
            )
            if ze_choix:
                lire(calice[ze_choix])
            else:
                if question_oui_non("Voulez vous que je lise tout ? "):
                    lire(str(" ".join(calice)))

                else:
                    lire(f"d'accord {self.pseudo}")

                _listbox.master.destroy()

    async def recup_infos(self):
        await self.recup_informations(20)

    async def recup_informations(self, max_article_a_recup: int = 10):
        """
        * récupère les motclés écrits dans motcle_widget sinon,
        * demande oralement à l'utilisateur de donner un motcle pour la recherche
        d'actualités

        """

        async def insert_article_to_grande_fenetre(motcle: str):
            if isinstance(recherche_articles, RechercheArticles):
                self.searchHystory.append(recherche_articles)
                t = StoppableThread(
                    target=await recherche_articles.insert_content_in_grande_fenetre(
                        motcles=motcle, grande_fenetre=self.grandeFenetre
                    ),
                )
                t.name = "find_articles"
                threads_outils.append(t)
                t.start()

        self.grandeFenetre = GrandeFenetre(tk.Toplevel(None))
        if len(self.get_motcles()):
            for element in self.get_motcles():
                mot, nb = element.split(":")
                recherche_articles: RechercheArticles = await self.extract_infos(
                    mot, int(nb) or max_article_a_recup
                )
                await insert_article_to_grande_fenetre(motcle=mot)

            self.reconfigure_aera()
            return recherche_articles.articles
        else:
            motcle = question_ouverte(
                "sur quel sujet voulez-vous que j'oriente mes recherches ?",
            )
            if motcle == "les sujets d'actualité":
                lire("Très bien, je récupère les actus en général")
                motcle = str()
            else:
                lire("Très bien, je récupère tout sur " + motcle)

            # récupération des titres du jour
            recherche_articles = await self.extract_infos(motcle, max_article_a_recup)

            lire(f"j'ai trouvé {recherche_articles.articles.__len__()} articles")

            await insert_article_to_grande_fenetre(motcle=motcle)

            self.reconfigure_aera()

            return motcle, recherche_articles.articles

    def reconfigure_aera(self):
        self.grandeFenetre.area_info.configure(
            height=min(
                reformat_text(self.grandeFenetre.area_info.get_text(), 30).__len__(), 60
            )
        )
        self.grandeFenetre.update()

    async def extract_infos(self, subject, max_article_a_recup: int):
        """
        * Transforme le texte récupéré en un **objet JSON**
        * instancie un objet rechercheArticles contenant tous les résultats
        de l'objet json
        * Pour chacun des résultats de recherche Valide, instancie un objet article et l'ajoute
        à la liste des articles de l'objet rechercheArticles
        * retourne l'objet rechercheArticle actualisé
        """
        _responses = get_news_api(subject)
        recherche_articles = RechercheArticles(
            status=_responses.json()["status"],
            articles=[],
            total_results=_responses.json()["totalResults"],
        )

        for n, article in enumerate(_responses.json()["articles"]):
            if n >= max_article_a_recup:
                break
            if "removed" not in str(article["title"]).lower():
                _transfert = Article(
                    source=article["source"],
                    author=article["author"],
                    title=article["title"],
                    description=article["description"],
                    url=article["url"],
                    url_to_image=article["urlToImage"],
                    published_at=article["publishedAt"],
                    content=article["content"],
                    image=await downloadimage(article["urlToImage"], 600),
                )
                recherche_articles.articles.append(_transfert)
                print(str(n) + "/" + str(max_article_a_recup) + " ; ")

        return recherche_articles

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
            conversation_resumee = await ask_to_resume(
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
            lire("un résumé des anciennes conversations à été effectué")
            if question_ouverte(
                "voulez-vous que je vous lise ce résumé ?",
            ):
                lire("Résumé des conversations précédente\n" + conversation_resumee)

        # Ajout de cette conversation dans la listes générale des conversations
        self.get_prompts_history().append(
            {
                "fenetre_name": fenetre_name,
                "prompt": ask_to_resume(self.get_client(), prompt, self.get_model()),
                "response": ask_to_resume(
                    self.get_client(), ai_response, self.get_model()
                ),
            },
        )

    async def check_before_read(self, response_to_read: str):
        """
        demande une confirmation avant de lire le résultat de la requette à haute voix
        """
        if self.get_ok_to_Read():
            lire(response_to_read)
        else:
            lire("voici !")

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

    # def attentif(self) -> str:
    #     """
    #     ### Méthode d'écoute attentive de ce qu'il se passe dans le micro
    #     * récupération du resultat et encapsulation dans un objet JSON
    #     * retourne la partie text de l'objet JSON pour traitement ou un texte VIDE
    #     """
    #     while True:
    #         try:
    #             data_real_pre_vocal_command = get_stream().read(
    #                 num_frames=8192, exception_on_overflow=False
    #             )

    #             if self.get_engine().AcceptWaveform(data_real_pre_vocal_command):

    #                 # récupération du resultat et encapsulation dans un objet JSON
    #                 # on renvoi la partie text de l'objet JSON
    #                 return json.loads(self.get_engine().Result())["text"].lower()
    #         except Exception as e:
    #             print(f"{e}")
    #             return (
    #                 simpledialog.askstring(
    #                     title="pas de micro", prompt="entrez votre commande"
    #                 )
    #                 or str()
    #             )

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

        lire("historique effacé !")

    def display_help(self) -> str:
        """
        affiche une fenetre d'aide
        """
        frame = tk.Toplevel(name="fenetre_aide")

        self.help_infos = SimpleMarkdownText(
            master=frame,
            width=len(max(LIST_COMMANDS, key=len)),
        )
        scrollbar_infos = tk.Scrollbar(frame)
        scrollbar_infos.configure(command=self.help_infos.yview)

        self.help_infos.pack(side=tk.LEFT, fill="both")

        for item in LIST_COMMANDS:
            self.help_infos.insert_markdown(item)

        self.help_infos.configure(
            background=from_rgb_to_tkcolors((40, 0, 40)),
            foreground=from_rgb_to_tkcolors(LIGHT2),
            yscrollcommand=scrollbar_infos.set,
            padx=20,
            pady=10,
            wrap="word",
            state="disabled",
        )

        scrollbar_infos.pack(side=tk.RIGHT, fill="both")

        _sortie = self.help_infos.bind(CLICK_LIST, func=self.lire_commande)
        return _sortie

    def call_display_listbox_actu(self, final_list, mode_audio: bool = False):
        _=self.display_listbox_actus(final_list, mode_audio=mode_audio)

    async def display_listbox_actus(self, final_list, mode_audio: bool = False):
        """
        ouvre une listbox avec toute les catégories d'informations disponibles à la recherche
        chaque clic appelle une focntion de recherche de la catégorie en question : demander_actu(),
        retourn self.get_submission() initialisée auparavant dans demander_actu()
        """
        try:
            frame = tk.Toplevel(name="list_actu")
            _list_box = tk.Listbox(
                master=frame,
                # on doit retirer le " | " autant de fois qu'il est présent
                # dans la ligne
                width=min(
                    100,
                    max(
                        map(
                            len,
                            [
                                str(element).replace(CATEGORY_SEPARATOR, ", ")
                                for element in final_list
                            ],
                        )
                    ),
                ),
                justify="left",
                height=min(final_list.__len__(), 15),
            )
            scrollbar_listbox = tk.Scrollbar(frame)
            scrollbar_listbox.configure(command=_list_box.yview)

            _list_box.pack(side=tk.LEFT, fill="both")

            for item in final_list:
                _list_box.insert(tk.END, item)

            _list_box.configure(
                background=from_rgb_to_tkcolors(LIGHT3),
                foreground=from_rgb_to_tkcolors(DARK3),
                yscrollcommand=scrollbar_listbox.set,
            )

            scrollbar_listbox.pack(side=tk.RIGHT, fill="both")

            if not mode_audio:
                _ = _list_box.bind(CLICK_LIST, func=self.lancement_infos)
            else:
                july = await self.get_audio_news(final_list)
                if not july:
                    frame.destroy()
                else:
                    lire("récupérations des actualités terminée")

        except Exception as e:
            print(f"{e}")
            lire("oups problème de liste d'information")

        finally:
            text_vocal_command = str()

        return self.get_submission(), text_vocal_command

    async def get_audio_news(self, final_list: list):
        final_list.append(ANNULE)
        response_rubrique = letters_to_number(
            question_ouverte(
                "Quelle rubrique voulez-vous que je recherche pour vous ?",
                choix=final_list,
            )
        )
        if response_rubrique:
            rubrique_info = RULS_RSS[int(response_rubrique)]
            lire(f"Parfait, je recherche des informations sur {rubrique_info["title"]}")
            feed_rss = recup_infos_rss_feed(
                content_selected=rubrique_info["content"],
                value=rubrique_info["title"],
            )

            translated_feeds = list(map(translate_it, feed_rss))
            for item in translated_feeds:
                print(f"Traduction auto --> {item}")

            lire(f"Il y aura {len(translated_feeds)} intitulés à récupérer")
            self.calice.clear()
            for i, subject in enumerate(translated_feeds):
                if str(subject).split().__len__() > 1:
                    kiki = await self.send_prompt(
                        content_discussion=make_resume(subject),
                        necessite_ai=True,
                        needed_groq=True,
                    )
                    self.set_submission(self.get_submission() + kiki)
                    self.calice.append(kiki)
                    # lire(f"Sujet {i}:   {str(subject)}")

                    time.sleep(4)
            self.display_search_list_results(self.calice)

        else:
            lire("Pardons, veuillez continuez")
            return False

    def lancement_infos(self, evt):
        _thread = StoppableThread(
            target=lambda: create_asyncio_task(self.demander_actu(evt))
        )
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

    async def send_prompt(
        self, content_discussion, necessite_ai: bool, needed_groq: bool
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
            if needed_groq:
                response, timing = await self.demander_ai_groq()
            else:
                response, timing = await self.demander_ai()

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

    async def demander_ai_groq(self) -> Tuple[str, float]:
        response, timing = await ask_to_ai(
            agent_appel=self.get_client(),
            prompt=self.get_submission(),
            model_to_use=self.get_model(),
            motcle=self.get_motcles(),
            p_history=self.get_prompts_history(),
        )
        return str(response), timing

    async def demander_ai(self) -> Tuple[str, float]:
        """vérifie aussi le texte pour faire des recherches web"""
        prompt = self.get_submission()
        if isinstance(prompt, list):
            prompt = "\n".join(prompt)  # Convertir en liste si c'est une chaîne de caractères

        response, timing = await ask_to_ai(
            self.get_client(),
            prompt,
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
                    + RESPONSE
                    + element["response"]
                    + "\n"
                )
            )
        return sortie

    async def asking(self) -> str:
        if self.get_debride():
            self.set_submission(" \n en mode débridé \n" + self.get_submission())

        response_ai, _timing = await ask_to_ai(
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
            lire("Fin de l'extraction")
            # on prepare le text pour le présenter à la méthode insert_markdown
            # qui demande un texte fait de lignes séparées par des \n
            # transforme list[str] -> str
            self.entree_prompt_principal.insert_markdown(mkd_text="".join(resultat_txt))

        except Exception as e:
            print(f"{e}")
            messagebox("Problème avec ce fichier txt")  # type: ignore

    def load_and_affiche_txt(self):
        resultat_txt: str = load_txt(self)
        self.entree_prompt_principal.insert_markdown(mkd_text=resultat_txt)

    def load_and_affiche_pdf(self):
        resultat_txt: str = load_pdf(self)
        self.entree_prompt_principal.insert_markdown(mkd_text=resultat_txt)

    def paste_clipboard(self):
        self.entree_prompt_principal.clear_text()
        self.entree_prompt_principal.insert_markdown(self.clipboard_get())

    def clear_entree_prompt_principal(self):
        self.entree_prompt_principal.clear_text()

    def traite_listbox(self, list_to_check: list, name: str = "list_ia") -> tk.Listbox:
        frame = tk.Toplevel(name=name)
        frame.grid_location(self.winfo_x() + 150, self.winfo_y() + 130)
        _list_box = tk.Listbox(
            master=frame,
            font=self.default_font,
            width=100,
            height=list_to_check.__len__(),
        )
        scrollbar_listbox = tk.Scrollbar(frame)
        scrollbar_listbox.configure(command=_list_box.yview)

        _list_box.pack(side=tk.LEFT, fill="both")
        for item in list_to_check:
            _list_box.insert(tk.END, item)
        _list_box.configure(
            background="red",
            foreground=from_rgb_to_tkcolors(DARK3),
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

            lire("en mode débridé, " + preprompt)

        except Exception as e:
            print(f"{e} : aucun préprompt sélectionné")
        finally:
            if w.focus_get() is not None:
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
            or str()
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
        _listbox.bind(CLICK_LIST, func=self.charge_preprompt)

    def creer_fenetre(self, msg_to_write):  # type: ignore
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
            background=from_rgb_to_tkcolors(DARK3)
        )
        self.frame_of_buttons_principal.pack(fill="x", expand=True)

        self.frame_actual_prompt = tk.Frame(
            self.master_frame_actual_prompt,
            relief="sunken",
            name="frame_actual_prompt",
            bg="black",
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
            bg=from_rgb_to_tkcolors(LIGHT0),
            fg=from_rgb_to_tkcolors(DARK3),
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
            bg=from_rgb_to_tkcolors(LIGHT3),
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
            command=self.entree_prompt_principal.yview, bg=from_rgb_to_tkcolors(DARK2)
        )

        # Création d'un bouton pour Lire
        self.bouton_lire1 = tk.Button(
            self.frame_of_buttons_principal,
            activebackground=from_rgb_to_tkcolors((255, 0, 0)),
            activeforeground=from_rgb_to_tkcolors((0, 255, 255)),
            relief="flat",
            font=self.btn_font,
            text=chr(9654),
            command=lambda: lire_text_from_object(object=self.entree_prompt_principal),
        )
        self.bouton_lire1.configure(
            bg=from_rgb_to_tkcolors(DARK3),
            fg=from_rgb_to_tkcolors(LIGHT3),
            highlightbackground="red",
            highlightcolor=from_rgb_to_tkcolors(LIGHT3),
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
            bg=from_rgb_to_tkcolors(DARK2),
            fg=from_rgb_to_tkcolors(LIGHT3),
            highlightbackground="red",
            highlightcolor=from_rgb_to_tkcolors(LIGHT3),
        )
        self.bouton_traduire_sur_place.pack(side=tk.LEFT)
        self.canvas_diction = tk.Canvas(self.frame_actual_prompt)

        # Création d'un bouton pour Dicter
        self.bouton_commencer_diction = tk.Button(
            self.canvas_diction,
            bg="black",
            image=self.image_button_diction1,  # type: ignore
            command=self.lance_thread_ecoute,
            relief="flat",
        )
        self.canvas_diction.pack(side=tk.LEFT, fill="x", expand=True)
        self.bouton_commencer_diction.pack(side=tk.TOP, fill="x", expand=True)

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
            bg=from_rgb_to_tkcolors(LIGHT3),
            highlightbackground="blue",
            highlightcolor=from_rgb_to_tkcolors(LIGHT3),
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
            bg=from_rgb_to_tkcolors(DARK1), fg=from_rgb_to_tkcolors(LIGHT3)
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
            bg=from_rgb_to_tkcolors(DARK2), fg=from_rgb_to_tkcolors(LIGHT3)
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
            bg=from_rgb_to_tkcolors(DARK3), fg=from_rgb_to_tkcolors((255, 255, 255))
        )
        self.bouton_load_txt.pack(side="left")

        self.widgetMotcles = tk.Entry(
            self.frame_of_buttons_principal,
            name="motcles_widget",
            relief="flat",
            width=50,
            fg="red",
            bg=from_rgb_to_tkcolors(DARK3),
            font=("trebuchet", 10, "bold"),
        )
        self.button_keywords = tk.Button(
            self.frame_of_buttons_principal,
            font=self.btn_font,
            text="📌",
            relief="flat",
            background=from_rgb_to_tkcolors(DARK2),
            foreground=from_rgb_to_tkcolors(LIGHT3),
            command=lambda: self.affiche_prepromts(PROMPTS_SYSTEMIQUES.keys()),  # type: ignore
        )
        self.button_keywords.pack(side=tk.RIGHT, expand=False)
        self.widgetMotcles.pack(side="left", fill="x", padx=2, pady=2)

    def textwidget_to_mp3(self):
        """
        #### txt vers mp3
        Transforme le text sélectionné dans l'object de type
        SimpleMarkdownText donné en parametre en dictée mp3.
            Si rien n'est sélectionné, tout le text est traité.
        """
        obj: SimpleMarkdownText = self.entree_prompt_principal

        if None == obj.get_selected():
            # on récupère tout le contenu de l'objet
            texte_to_save_to_mp3 = obj.get("1.0", tk.END)
        else:
            texte_to_save_to_mp3 = obj.get_selected()

        if None != texte_to_save_to_mp3:
            if len(str(texte_to_save_to_mp3)) > 0:

                lire("transcription du texte vers un fichier mp3")
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
                lire("terminé")
        else:
            print("rien à transformer")

    def replace_in_place(self, texte: str, index1: str, index2: str):
        """traduit sur place (remplacement) le texte sélectionné"""
        self.entree_prompt_principal.replace(chars=texte, index1=index1, index2=index2)

    def traduit_maintenant(self):
        self.set_timer(float(time.perf_counter_ns()))
        translated_text = self.entree_prompt_principal.get_selected()

        if translated_text is not None:
            indx1 = self.entree_prompt_principal.index(tk.SEL_FIRST)
            indx2 = self.entree_prompt_principal.index(tk.SEL_LAST)
            texte_traite = traitement_du_texte(str(translated_text))
            if isinstance(texte_traite, list):
                for element in texte_traite:
                    translated_text = str(translate_it(text_to_translate=element))
                    self.replace_in_place(
                        texte=translated_text,
                        index1=indx1,
                        index2=indx2,
                    )

            else:
                _result = str(translate_it(text_to_translate=texte_traite))
                self.replace_in_place(
                    texte=_result,
                    index1=indx1,
                    index2=indx2,
                )

        else:
            texte_traite = traitement_du_texte(self.entree_prompt_principal.get_text())

            if isinstance(texte_traite, list):
                sortie = str()
                for element in texte_traite:
                    translated_text = str(translate_it(text_to_translate=element))
                    sortie += "\n" + translated_text

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

        lire("fin de la traduction")

    def load_selected_model(self, evt: tk.Event):
        # Note here that Tkinter passes an event object to onselect()
        w: tk.Listbox = evt.widget
        try:
            index = w.curselection()[0]
            value = w.get(index)
            print(YOU_SELECT_VALUE % (index, value))
            self.set_model(name_ia=str(value))
            _widget: tk.Button = self.nametowidget("cnvs1.cnvs2.btnlist")
            _widget.configure(text=value)
            lire("ok")
        except Exception as e:
            print(f"{e} : aucune ia sélectionner")
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
        feed_rss = []
        try:
            index = w.curselection()[0]

            value = str(w.get(index)).split(" :: ")[0]

            print('You selected item %d: "%s"' % (index, value))
            content_selected = [
                item["content"]
                for item in RULS_RSS
                if item["title"].lower() == value.lower()
            ].pop()

            feed_rss = recup_infos_rss_feed(
                content_selected=content_selected, value=value
            )
            if feed_rss.__len__():
                for item in feed_rss:
                    print(f"--> {item}")

                lire(f"Il y aura {len(feed_rss)} intitulés à récupérer")
                for i, subject in enumerate(feed_rss):
                    if subject.__len__():
                        kiki = await self.send_prompt(
                            content_discussion=make_resume(subject),
                            necessite_ai=True,
                            needed_groq=True,
                        )
                        self.set_submission(self.get_submission() + kiki)
                        # lire(f"Sujet {i}:   {str(subject)}")

                        time.sleep(4)

                lire("Récupération terminée")
                self.display_search_list_results(feed_rss)

        except Exception as e:
            error_msg = (
                f"Problème pour récupérer les infos (index:{index},value:{value})"
            )
            messagebox.showerror("OOps, ", error_msg)
            logger.exception(msg=error_msg, exc_info=e)
            logger.error("OOps, ", error_msg)
            raise e

    def lire_commande(self, evt: tk.Event):

        # Note here that Tkinter passes an event object to onselect()
        w: tk.Listbox = evt.widget
        index = w.curselection()[0]
        value = w.get(index)
        print('You selected item %d: "%s"' % (index, value))
        lire(value)

    def affiche_ia_list(self, list_to_check: list):
        """
        Display a list of AI you can use
        * affiche la listebox avec la liste donnée en paramètre list_to_check
        * click on it cause model AI to change
        """
        _listbox: tk.Listbox = self.traite_listbox(list_to_check)
        _listbox.bind(CLICK_LIST, func=self.load_selected_model)

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
        except Exception as e:
            print(f"{e} ==> la fentre {conversation.id} est déjà effacée")
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
                + RESPONSE
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
                + RESPONSE
                + str(julia[:59] + "...\n" if len(julia) >= 60 else julia + "\n")
            )
        print("************************************")
