import asyncio
import json
import time
from tkinter import filedialog, messagebox, simpledialog
from typing import Any
import ollama
from llama_index.llms.ollama import Ollama as Ola
import pyaudio
from Constants import *
import tkinter.font as tkfont
import tkinter as tk
import vosk
from PIL import Image, ImageTk
import threading
import pyttsx3

from FenetreResponse import FenetreResponse
from FenetreScrollable import FenetreScrollable
from SimpleMarkdownText import SimpleMarkdownText
from StoppableThread import StoppableThread
from outils import (
    actualise_index_html,
    append_response_to_file,
    display_infos_model,
    engine_lecteur_init,
    from_rgb_to_tkColors,
    get_pre_prompt,
    lire_text_from_object,
    load_pdf,
    load_txt,
    read_prompt_file,
    say_txt,
    traitement_du_texte,
    translate_it,
)


class FenetrePrincipale(tk.Frame):
    master: tk.Tk
    content: str
    title: str
    ia: str
    submission: str
    talker: any
    model_to_use: str
    streaming: pyaudio.Stream
    engine_model: vosk.KaldiRecognizer
    image: ImageTk
    image_link: str
    motcle: list[str]
    client: any = None
    ai_response: str
    timer: float
    thread: threading.Thread

    def __init__(
        self,
        stream: pyaudio.Stream,
        model_to_use: str,
        master,
    ):
        super().__init__(master)
        self.master = master
        self.ia = LLAMA3
        self.submission = ""
        self.talker = say_txt
        self.lecteur = engine_lecteur_init()
        self.model_to_use = model_to_use
        self.streaming = stream
        self.image = ImageTk.PhotoImage(
            Image.open("banniere.jpeg").resize((BANNIERE_WIDTH, BANNIERE_HEIGHT))
        )
        self.image_link = ""
        self.content = ""
        self.configure(padx=5, pady=5, width=FENETRE_WIDTH + 10)
        self.pack()
        self.creer_fenetre(
            image=self.get_image(),
            msg_to_write="Veuillez écrire ou coller ici le texte à me faire lire...",
        )
        self.fenetre_scrollable = FenetreScrollable(self)
        self.fenetre_scrollable.configure(width=BANNIERE_WIDTH)
        self.fenetre_scrollable.pack(side="bottom", fill="both", expand=False)
        self.my_liste = []
        for element in (ollama.list())["models"]:
            self.my_liste.append(element["name"])

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
        self.get_talker()("changement du client : " + str(type(self.client)))

    def get_client(self) -> Any:
        return self.client

    def set_motcle(self, motcle: list[str]):
        self.motcle = motcle

    def get_motcle(self) -> list[str]:
        return self.motcle

    def set(self, content: str):
        self.content = content

    def get(self) -> str:
        return self.content

    def get_talker(self) -> pyttsx3.Engine:
        return self.talker

    def set_talker(self, talker: pyttsx3.Engine):
        self.talker = talker

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
        self.get_talker()("changement d'ia: " + self.model_to_use)

    def get_model(self) -> str:
        return self.model_to_use

    def get_stream(self) -> pyaudio.Stream:
        return self.streaming

    def set_engine(self, engine):
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
        # récupère le texte contenu dans le widget_mot_clé
        speciality = self.motcles_widget.get()  # if motcles_widget.get() else ""

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
            canvas_buttons_banniere, text="Quitter", command=quitter_app
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
            command=lambda: self.affiche_ia_list(self.my_liste),
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

    def soumettre(self) -> str:
        if self.save_to_submission():
            self.get_talker()("un instant s'il vous plait")
            threading.Thread(target=self.start_loop).start()

        elif not threading.current_thread().is_alive():
            self.set_submission("")

        else:
            messagebox.showinfo(message="Veuillez poser au moins une question")

    def lance_ecoute(self):
        self.bouton_commencer_diction.flash()
        my_thread = threading.Thread(name="my_thread", target=self.ecouter)
        my_thread.start()

    def ecouter(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(self.dialog_ia())
        loop.run_forever()

    # TODO : problème ici, difficulté à arrêter le thread !!
    async def dialog_ia(self):
        print("on est dans l'async def dialog_ia")
        terminus = False
        content_discussion = ""

        while not terminus:
            reco_text = ""
            chating = False
            data = self.get_stream().read(
                num_frames=8192, exception_on_overflow=False
            )  # read in chunks of 4096 bytes
            if self.get_engine().AcceptWaveform(data):  # accept waveform of input voice

                # Parse the JSON result and get the recognized text
                result = json.loads(self.get_engine().Result())
                reco_text: str = result["text"]
                print(reco_text)
                if "dis-moi" == reco_text.lower() or chating:
                    print("je t'écoute")
                    say_txt("je t'écoute")
                    reco_text_real = ""
                    content_discussion = ""
                    while True:

                        start_tim_vide = time.perf_counter()
                        start_tim_parlotte = time.perf_counter()
                        data_real = self.get_stream().read(
                            num_frames=8192, exception_on_overflow=False
                        )  # read in chunks of 4096 bytes
                        if self.get_engine().AcceptWaveform(
                            data_real
                        ):  # accept waveform of input voice
                            # Parse the JSON result and get the recognized text
                            result_real = json.loads(self.get_engine().Result())
                            reco_text_real: str = result_real["text"]

                            ne_pas_deranger = (
                                "ne pas déranger" in reco_text_real.lower()
                            )
                            activer_parlote = (
                                "activer la voix" in reco_text_real.lower()
                            )
                            incremente_lecteur = (
                                "la voie soit plus rapide" in reco_text_real.lower()
                            )
                            decremente_lecteur = (
                                "la voie soit moins rapide" in reco_text_real.lower()
                            )

                            if incremente_lecteur:
                                engine = self.lecteur
                                engine.setProperty(
                                    name="rate",
                                    value=int(engine.getProperty(name="rate")) + 20,
                                )
                                reco_text_real = ""
                                say_txt("voix plus rapide")

                            if decremente_lecteur:
                                self.lecteur.setProperty(
                                    name="rate",
                                    value=int(self.lecteur.getProperty(name="rate"))
                                    + -20,
                                )
                                reco_text_real = ""
                                say_txt("voix plus lente")

                            if ne_pas_deranger:
                                reco_text_real = ""
                                say_txt("ok plus de bruit")
                                STOP_TALKING = True

                            if activer_parlote:
                                STOP_TALKING = False
                                reco_text_real = ""
                                say_txt("ok me re voilà")

                            if "quel jour sommes-nous" in reco_text_real.lower():
                                reco_text_real = ""
                                say_txt(
                                    "Nous sommes le " + time.strftime("%Y-%m-%d"),
                                )

                            if "quelle heure est-il" in reco_text_real.lower():
                                reco_text_real = ""
                                say_txt(
                                    "il est exactement " + time.strftime("%H:%M:%S"),
                                )

                            if "est-ce que tu m'écoutes" in reco_text_real.lower():
                                reco_text_real = ""
                                say_txt("oui je suis toujours à l'écoute kiki")

                            if (
                                "terminer l'enregistrement" == reco_text_real.lower()
                                or "fin de l'enregistrement" == reco_text_real.lower()
                                or "arrêter l'enregistrement" == reco_text_real.lower()
                            ):
                                reco_text_real = ""
                                # terminus = True
                                stop_thread = StoppableThread(
                                    None, threading.current_thread()
                                )
                                if not stop_thread.stopped():
                                    stop_thread.stop()
                                self.entree_prompt_principal.insert_markdown(
                                    mkd_text="\n" + content_discussion + "\n"
                                )
                                break
                            elif reco_text_real.lower() != "":
                                start_tim_vide = time.perf_counter()
                                content_discussion += "\n" + reco_text_real.lower()
                                print("insertion de texte")
                                self.entree_prompt_principal.update()

                        time_delta_vide = time.perf_counter() - start_tim_vide
                        time_delta_parlotte = time.perf_counter() - start_tim_parlotte
                        print(str(time_delta_vide) + " :: " + str(time_delta_parlotte))

                    stop_thread = StoppableThread(None, threading.current_thread())
                    if not stop_thread.stopped():
                        stop_thread.stop()
                    self.entree_prompt_principal.update()
                if "validez" == reco_text.lower() or "terminez" == reco_text.lower():
                    self.set_submission(content=content_discussion)
                    stop_thread = StoppableThread(None, threading.current_thread())
                    if not stop_thread.stopped():
                        stop_thread.stop()
                    response, timing = self.ask_to_ai(
                        self.get_client(), self.get_submission(), self.get_model()
                    )
                    fenetre_response = FenetreResponse(
                        master=self.fenetre_scrollable(self),
                        entree_recup=self.entree_prompt_principal,
                        ai_response=response,
                    )
                    fenetre_response.pack(side=tk.BOTTOM, fill="both", expand=True)
                    fenetre_response.entree_response.insert_markdown(response)
                    say_txt(response)
                    # on sort du tchat une fois répondu
                    # sinon des erreurs sont levées
                    chating = False
                if "fin de la session" == reco_text.lower():
                    terminus
                    chating = False
                    break

    def start_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("LOOOOOOOOOOOOOOOOOOOPPPPEEEEEEEEEERRRRRRRRR")
        loop.run_until_complete(loop.create_task(self.asking()))
        loop.close()

    def go_submit(self, evt):
        self.soumettre()

    def ask_to_ai(self, agent_appel, prompt, model_to_use):

        self.set_timer(time.perf_counter_ns())

        if isinstance(agent_appel, ollama.Client):
            try:
                llm: ollama.Client = agent_appel.chat(
                    model=model_to_use,
                    messages=[
                        {
                            "role": ROLE_TYPE,
                            "content": prompt,
                            "num_ctx": 4096,
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

        elif isinstance(agent_appel, Ola.__class__):
            try:
                llm: Ola = agent_appel(
                    base_url="http://localhost:11434",
                    model=model_to_use,
                    request_timeout=REQUEST_TIMEOUT_DEFAULT,
                    additional_kwargs={
                        "num_ctx": 4096,
                        "num_predict": 40,
                        "keep_alive": -1,
                    },
                )
                ai_response = llm.chat(prompt).message.content
            except:
                messagebox.Message("OOps, ")

        # calcul le temps écoulé par la thread
        timing: float = (time.perf_counter_ns() - self.get_timer()) / 1_000_000_000.0
        print(ai_response)
        print("Type_agent_appel::" + str(type(agent_appel)))
        print("Type_ai_réponse::" + str(type(ai_response)))

        append_response_to_file(RESUME_WEB, ai_response)
        actualise_index_html(
            texte=ai_response, question=prompt, timing=timing, model=self.get_model()
        )

        return ai_response, timing

    async def asking(self) -> asyncio.futures.Future:
        # ici on pourra pointer sur un model hugginface plus rapide à répondre mais en ligne

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
            simple_markdown=self.entree_prompt_principal,
            ai_response=response_ai,
            talker=self.get_talker(),
            model=self.get_model(),
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
            resultat_txt = read_prompt_file(file_to_read.name)
            self.get_talker()("Fin de l'extraction")

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

    def traite_listbox(self, list_to_check: list):
        frame = tk.Tk(className="list_ia")
        frame.grid_location(self.winfo_x() + 50, self.winfo_y() + 30)
        _list_box = tk.Listbox(frame)
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
                prompt_name=str(self.get_motcle()).lower(),
            )
            self.set_submission(preprompt)

            self.get_talker()("prépromt ajouté : " + preprompt)

        except:
            print("aucun préprompt sélectionné")
            self.get_talker()("Oups")
        finally:
            w.focus_get().destroy()

    def affiche_prepromts(self, list_to_check: list):
        """Diplays premprompts
        * asking for keywords about this subject
        * enregistre ces mot-cles dans l'attribut motcle de la classe app.
        * puis les insère dans <motcles_widget> de la fenetre principal
        * affiche la listebox avec la liste donnée en paramètre list_to_check

        ### TODO : make it possible to display the prompt directly when clic of or when hovering over the prompt categories
        """
        # ouvre une boite dialog et récupère la sortie
        mots_cle = simpledialog.askstring(
            title="YourAssistant - pré-prompts",
            initialvalue="Python",
            prompt="Veuillez entrer le mot-clé à traiter",
        )

        # on set l'attribut motcle de la classe
        self.set_motcle(mots_cle.split())

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

        def textwidget_to_mp3(object: tk.Text):
            texte_to_save_to_mp3 = object.get("1.0", tk.END)

            if texte_to_save_to_mp3 != "":
                try:
                    texte_to_save_to_mp3 = object.get(tk.SEL_FIRST, tk.SEL_LAST)
                except:
                    texte_to_save_to_mp3 = object.get("1.0", tk.END)
                finally:
                    self.get_talker()("transcription du texte vers un fichier mp3")
                    simple_dialog = simpledialog.askstring(
                        parent=self,
                        prompt="Enregistrement : veuillez choisir un nom au fichier",
                        title="Enregistrer vers audio",
                    )
                    self.lecteur.save_to_file(
                        texte_to_save_to_mp3, simple_dialog.lower() + ".mp3"
                    )
                    self.get_talker()("terminé")
            else:
                self.get_talker()("Désolé, Il n'y a pas de texte à enregistrer en mp3")

        def replace_in_place(
            texte: str, index1: str, index2: str, ponctuel: bool = True
        ):
            self.entree_prompt_principal.replace(
                chars=texte, index1=index1, index2=index2
            )

        def translate_inplace():
            traduit_maintenant()

        def traduit_maintenant():
            was_a_list = False
            try:
                # TRANSLATE IN PLACE
                texte_initial = self.entree_prompt_principal.get(
                    tk.SEL_FIRST, tk.SEL_LAST
                )
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
                        sortie += translated_text
                    was_a_list = True

                    self.fenetre_scrollable.addthing(
                        _timing=0,
                        agent_appel=any,
                        simple_markdown=self.entree_prompt_principal,
                        ai_response=sortie,
                        talker=self.get_talker(),
                        model=self.get_model(),
                    )
                elif was_a_list == True:
                    translated_text = str(translate_it(text_to_translate=texte_traite))
                    self.fenetre_scrollable.addthing(
                        _timing=0,
                        agent_appel=any,
                        simple_markdown=self.entree_prompt_principal,
                        ai_response=translated_text,
                        talker=self.get_talker(),
                        model=self.get_model(),
                    )
                else:
                    translated_text = str(translate_it(text_to_translate=texte_traite))
                    self.fenetre_scrollable.addthing(
                        _timing=0,
                        agent_appel=any,
                        simple_markdown=self.entree_prompt_principal,
                        ai_response=translated_text,
                        talker=self.get_talker(),
                        model=self.get_model(),
                    )

                self.get_talker()("fin de la traduction")

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
            background=from_rgb_to_tkColors(DARK3)
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
        self.boutton_effacer_entree_prompt_principal.configure(
            bg="red", fg=from_rgb_to_tkColors(LIGHT3)
        )
        self.boutton_effacer_entree_prompt_principal.pack(side="right")
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

        # Création d'un bouton pour Lire
        self.bouton_lire1 = tk.Button(
            self.frame_of_buttons_principal,
            text="Lire",
            command=lambda: lire_text_from_object(self.entree_prompt_principal),
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
            self.frame_of_buttons_principal, text=" ф ", command=self.lance_ecoute
        )
        self.bouton_commencer_diction.configure(
            bg="red", fg=from_rgb_to_tkColors(LIGHT3)
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

        # TODO NE fonctionne pas pour mettre en pause la lecture à haute voix
        # bouton_stop=tk.Button(frame_of_buttons_principal,text="Stop",command=lecteur.endLoop)
        # bouton_reprendre=tk.Button(frame_of_buttons_principal,text="reprendre",command=lecteur.startLoop)
        # bouton_stop.pack(side=tk.LEFT)
        # bouton_reprendre.pack(side=tk.LEFT)

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
            model_info = ollama.show(self.get_model())
            self.get_talker()("ok")
            display_infos_model(master=self.nametowidget("cnvs1"), content=model_info)
        except:
            print("aucune ia sélectionner")
            self.get_talker()("Oups")
        finally:
            w.focus_get().destroy()

    def affiche_ia_list(self, list_to_check: list):
        """
        Display a list of AI you can use
        * affiche la listebox avec la liste donnée en paramètre list_to_check
        * click on it cause model AI to change
        """
        _listbox: tk.Listbox = self.traite_listbox(list_to_check)
        _listbox.bind("<<ListboxSelect>>", func=self.load_selected_model)