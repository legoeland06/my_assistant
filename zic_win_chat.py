# zic_chat.py
from argparse import Namespace
import asyncio
import datetime
import json.tool
import re
import threading
import time
import tkinter as tk
from tkinter import Event, StringVar, messagebox
from tkinter import filedialog
from tkinter import simpledialog
import tkinter.font as tkfont
import tkinter.scrolledtext as tkscroll
from typing import Any, Mapping
import PyPDF2
from tkhtmlview import HTMLLabel
from PIL import Image, ImageTk
import markdown.util
import vosk
import pyaudio
import json
import pyttsx3
import ollama
from llama_index.llms.ollama import Ollama as Ola
import markdown
import imageio.v3 as iio
import subprocess
from spacy.lang.fr import French
from spacy.lang.en import English
from PIL import Image, ImageTk
from SimpleMarkdownText import SimpleMarkdownText
from StoppableThread import StoppableThread
from Constants import *


def get_pre_prompt(rubrique: str, prompt_name: str):
    return PROMPTS_SYSTEMIQUES[rubrique].replace(rubrique, prompt_name)


def affiche_preprompts():
    print(INFOS_PROMPTS)
    print(STARS * WIDTH_TERM)
    for preprompt in PREPROMPTS:
        print(str(PREPROMPTS.index(preprompt)) + ". " + preprompt)


def engine_lecteur_init():
    """
    ## initialise le Lecteur de l'application
    * initialise pyttsx3 avec la langue française
    * set la rapidité de locution.
    #### RETURN : lecteur de type Any|Engine
    """
    lecteur = pyttsx3.init()
    lecteur.setProperty("lang", "french")
    lecteur.setProperty("rate", RAPIDITE_VOIX)

    # TODO Rien à faire ici, voir si on peut le déplacer
    pyttsx3.speak("lancement...")

    return lecteur


def read_pdf(book):
    text = ""
    pdf_Reader = PyPDF2.PdfReader(book)
    pages = pdf_Reader.pages
    for page in pages:
        text += page.extract_text() + "\n"
    return text


def lancer_chrome(url: str) -> subprocess.Popen[str]:
    return subprocess.Popen(
        GOOGLECHROME_APP + url,
        text=True,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def tester_appellation(appelation: str) -> str:
    for lien in LIENS_CHROME:
        if lien in appelation:
            chrome_pid = lancer_chrome(url=LIENS_CHROME[lien])
            return lien


def engine_ecouteur_init():
    # set verbosity of vosk to NO-VERBOSE
    vosk.SetLogLevel(-1)
    # Initialize the model with model-path
    return vosk.Model(MODEL_PATH, lang="fr-fr")


def init_model(model_to_use: str, prompted: bool = False):
    # model utilisé dans le chatbot
    msg = (
        "Chargement de l'Ia : ["
        + model_to_use[0 : model_to_use.find(":")]
        + "]... Un instant"
    )
    print(msg)
    if not prompted:
        lecteur.say(msg)
        lecteur.runAndWait()
        lecteur.stop()
    return model_to_use


def lire_fichier(file_name: str) -> str:

    with open(file_name + ".txt", "r", encoding="utf-8") as file:
        if file.readable():
            data_file = file.read().rstrip()
            return "fais moi un résumé de ce texte: " + data_file
        else:
            return ""


def lire_url(url: str) -> str:
    return url


def lire_image(name: str) -> any:
    # Load a single image
    im = iio.imread(name)
    print(im.shape)  # Shape of the image (height, width, channels)
    return im


def make_choice(moteur_de_diction, iterable: iter):
    moteur_de_diction(ASK_TASK)
    print("\nMENU\n" + STARS * WIDTH_TERM)
    for question in iterable:
        print(str(iterable.index(question)) + ". " + question)
    choix = input(STARS * WIDTH_TERM + "\nVotre choix: ")
    if choix.isnumeric and len(choix) <= 2:
        moteur_de_diction(iterable[int(choix)])
        return iterable[int(choix)]
    elif choix.isalpha and len(choix) > 2:
        return choix
    else:
        return QUIT_MENU_COMMAND


def make_choice_dict(moteur_de_diction, dicto: dict):
    moteur_de_diction(ASK_TASK)
    print("\nMENU\n" + STARS * WIDTH_TERM)
    inc = 0
    for item in dicto.items():
        item_in_list = list(item)
        if len(item_in_list[1]) > 80:
            print(
                str(inc)
                + ". "
                + item_in_list[0]
                + " :: "
                + item_in_list[1][:80]
                + " ..."
            )
        else:
            print(str(inc) + ". " + item_in_list[0] + " :: " + item_in_list[1])
        inc += 1

    choix_ecrit = input(STARS * WIDTH_TERM + "\nVotre choix_ecrit: ")

    if choix_ecrit.isnumeric and len(choix_ecrit) <= 2:
        choix_reel = list(dicto.items())[int(choix_ecrit)]
        choix_detail = choix_reel[1]
        choix_intitule = choix_reel[0]
        moteur_de_diction(choix_intitule)
        return choix_intitule, choix_detail
    elif choix_ecrit.isalpha and len(choix_ecrit) > 2:
        return choix_ecrit, ""
    else:
        return QUIT_MENU_COMMAND, ""


def veullez_patienter(moteur_de_diction):
    moteur_de_diction(TRAITEMENT_EN_COURS, stop_ecoute=True)


def merci_au_revoir(
    moteur_de_diction,
    stream_to_stop: pyaudio.Stream,
    pulse_audio_to_stop: pyaudio.PyAudio,
):
    # Stop and close the stream_to_stop
    moteur_de_diction(BYEBYE, False)
    lecteur.stop()
    stream_to_stop.stop_stream()
    stream_to_stop.close()
    # Terminate the PyAudio object
    pulse_audio_to_stop.terminate()
    exit(0)


def au_revoir():
    exit(0)


def traitement_chat(moteur_de_diction):
    result = mode_chat(moteur_de_diction)
    if result == QUIT_MENU_COMMAND:
        return QUIT_MENU_COMMAND, moteur_de_diction
    if result == "/x":
        result, _ = mode_Super_chat(moteur_de_diction)
    return result, moteur_de_diction


def mode_chat(moteur_de_diction):
    moteur_de_diction("Mode tchat activé", False)
    # print("Mode chat activé")
    return input(" ==> ")


def mode_Super_chat(moteur_de_diction):
    moteur_de_diction("Mode multilignes activé", False)
    buffer = []
    while True:
        try:
            line = input()
            if line == "f.d.c.p":
                return "\n".join(buffer), moteur_de_diction
            elif line == EXIT_APPLICATION_COMMAND:
                au_revoir()
            elif line == QUIT_MENU_COMMAND:
                return "", moteur_de_diction
        except EOFError:
            break
        buffer.append(line)

    multiline_string = "\n".join(buffer)
    return multiline_string, moteur_de_diction


def append_response_to_file(file_to_append, readable_ai_response):
    with open(file_to_append + ".html", "a", encoding="utf-8") as target_file:
        markdown_content = markdown.markdown(
            readable_ai_response, output_format="xhtml"
        )
        target_file.write(markdown_content + "\n")
    with open(file_to_append + ".md", "a", encoding="utf-8") as target_file:
        markdown_content = markdown.markdown(
            readable_ai_response, output_format="xhtml"
        )
        target_file.write(markdown_content + "\n")
    with open(file_to_append + ".txt", "a", encoding="utf-8") as target_file:
        markdown_content = readable_ai_response
        target_file.write(
            "::"
            + datetime.datetime.now().isoformat()
            + "::\n"
            + markdown_content
            + "\n"
        )


def ask_to_ai(agent_appel, prompt, model_to_use):

    app.set_timer(time.perf_counter_ns())

    if isinstance(agent_appel, ollama.Client):
        llm: ollama.Client = agent_appel.chat(
            model=model_to_use,
            messages=[
                {
                    "role": ROLE_TYPE,
                    "content": prompt,
                },
            ],
        )
        ai_response = llm["message"]["content"]

    elif isinstance(agent_appel, Ola.__class__):
        llm: Ola = agent_appel(
            base_url="http://localhost:11434",
            model=model_to_use,
            request_timeout=3600,
            additional_kwargs={"num_predict": 1024, "keep_alive": -1},
        )
        ai_response = llm.complete(prompt).text

    # calcul le temps écoulé par la thread
    timing: float = (time.perf_counter_ns() - app.get_timer()) / 1000.0
    print("Type_agent_appel::" + str(type(agent_appel)))
    print("Type_ai_réponse::" + str(type(ai_response)))

    append_response_to_file(resume_web_page, ai_response)
    actualise_index_html(texte=ai_response, question=prompt)

    return ai_response, timing


def traitement_rapide(texte: str, model_to_use, talking: bool, moteur_diction):
    ai_response, _timing = ask_to_ai(
        agent_appel=ollama.Client, prompt=texte, model_to_use=model_to_use
    )
    readable_ai_response = ai_response
    app.get_talker()(readable_ai_response, False)


class Fenetre_entree(tk.Frame):
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

    def __init__(
        self,
        stream: pyaudio.Stream,
        model_to_use: str,
        master=None,
    ):
        super().__init__(master)
        self.master = master
        self.pack()
        self.title = root.winfo_name()
        self.ia = LLAMA3
        self.submission = ""
        self.talker = say_txt
        self.model_to_use = model_to_use
        self.streaming = stream
        self.image = ImageTk.PhotoImage(
            Image.open("banniere.jpeg").resize((BANNIERE_WIDTH, BANNIERE_HEIGHT))
        )
        self.image_link = ""
        self.content = ""
        self.configure(height=800)
        # self.set_client(ollama)
        self.creer_fenetre(
            image=self.get_image(),
            msg_to_write="Veuillez écrire ou coller ici le texte à me faire lire...",
        )

    def set_timer(self, timer: float):
        self.timer = timer

    def get_timer(self) -> float:
        return self.timer

    def set_ai_response(self, response: str):
        self.ai_response = response

    def get_ai_response(self) -> str:
        return self.ai_response

    # ici on pourra pointer sur un model hugginface plus rapide à répondre mais en ligne
    def set_client(self, client: ollama.Client):
        self.client = client
        pyttsx3.speak("changement du client : " + str(type(self.client)))

    def get_client(self) -> ollama.Client:
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

    def set_talker(self, talker):
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
        pyttsx3.speak("changement d'ia: " + self.model_to_use)

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

    # open a windows
    def creer_fenetre(self, image: ImageTk, msg_to_write):

        def lance_ecoute():
            bouton_commencer_diction.flash()
            my_thread = threading.Thread(name="my_thread", target=ecouter)
            my_thread.start()

        def ecouter():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.create_task(dialog_ia())
            loop.run_forever()

        # TODO : problème ici, difficulté à arrêter le thread !!
        async def dialog_ia():
            print("on est dans l'async def dialog_ia")
            terminus = False
            while not terminus:
                reco_text = ""
                data = self.get_stream().read(
                    num_frames=8192, exception_on_overflow=False
                )  # read in chunks of 4096 bytes
                if self.get_engine().AcceptWaveform(
                    data
                ):  # accept waveform of input voice

                    # Parse the JSON result and get the recognized text
                    result = json.loads(self.get_engine().Result())
                    reco_text: str = result["text"]
                    print(reco_text)
                    if "dis-moi" == reco_text.lower():
                        print("je t'écoute")
                        self.get_talker("je t'écoute", False)
                        reco_text_real = ""
                        while not terminus:
                            if "fin de l'enregistrement" in reco_text_real.lower():
                                terminus = True
                                stop_thread = StoppableThread(
                                    None, threading.current_thread()
                                )
                                if not stop_thread.stopped():
                                    stop_thread.stop()
                                break

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
                                    "la voie soit moins rapide"
                                    in reco_text_real.lower()
                                )

                                if incremente_lecteur:
                                    engine = lecteur
                                    engine.setProperty(
                                        name="rate",
                                        value=int(engine.getProperty(name="rate")) + 20,
                                    )
                                    self.get_talker("voix plus rapide", False)

                                if decremente_lecteur:
                                    lecteur.setProperty(
                                        name="rate",
                                        value=int(lecteur.getProperty(name="rate"))
                                        + -20,
                                    )
                                    self.get_talker("voix plus lente", False)

                                if ne_pas_deranger:
                                    self.get_talker("ok plus de bruit", False)
                                    STOP_TALKING = True

                                if activer_parlote:
                                    STOP_TALKING = False
                                    self.get_talker("ok me re voilà", False)

                                if "quel jour sommes-nous" in reco_text_real.lower():
                                    self.get_talker(
                                        "Nous sommes le " + time.strftime("%Y-%m-%d"),
                                        False,
                                    )

                                if "quelle heure est-il" in reco_text_real.lower():
                                    self.get_talker(
                                        "il est exactement "
                                        + time.strftime("%H:%M:%S"),
                                        False,
                                    )

                                if "est-ce que tu m'écoutes" in reco_text_real.lower():
                                    self.get_talker(
                                        "oui je suis toujours à l'écoute kiki", False
                                    )

                                if (
                                    "terminer l'enregistrement"
                                    == reco_text_real.lower()
                                    or "fin de l'enregistrement"
                                    == reco_text_real.lower()
                                    or "arrêter l'enregistrement"
                                    == reco_text_real.lower()
                                ):
                                    reco_text_real = ""
                                    break
                                elif reco_text_real.lower() != "":
                                    start_tim_vide = time.perf_counter()
                                    entree1.insert_markdown(
                                        mkd_text=reco_text_real + "\n"
                                    )
                                    print("insertion de texte")
                                    entree1.update()
                            if "fin de l'enregistrement" in reco_text_real.lower():
                                terminus = True
                                break

                            time_delta_vide = time.perf_counter() - start_tim_vide
                            time_delta_parlotte = (
                                time.perf_counter() - start_tim_parlotte
                            )
                            print(
                                str(time_delta_vide) + " :: " + str(time_delta_parlotte)
                            )

                        stop_thread = StoppableThread(None, threading.current_thread())
                        if not stop_thread.stopped():
                            stop_thread.stop()
                        entree1.update()
                    if terminus:
                        break
            stop_thread = StoppableThread(None, threading.current_thread())
            if not stop_thread.stopped():
                stop_thread.stop()

        def start_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(loop.create_task(asking()))

        def go_submit(evt):
            soumettre()

        def soumettre() -> str:
            if save_to_submission():
                self.talker("un instant s'il vous plait", False)
                threading.Thread(target=start_loop).start()

            elif not threading.current_thread().is_alive():
                self.set_submission("")

            else:
                messagebox.showinfo(message="Veuillez poser au moins une question")

        async def asking() -> asyncio.futures.Future:
            # ici on pourra pointer sur un model hugginface plus rapide à répondre mais en ligne

            if not self.get_client():
                messagebox.showerror(
                    title="Client absent",
                    message="Vous devez choisir un client, en haut à gauche de l'écran",
                )
                return
            agent_appel = self.get_client()

            response_ai, _timing = ask_to_ai(
                agent_appel=agent_appel,
                model_to_use=self.get_model(),
                prompt=self.get_submission(),
            )
            readable_ai_response = response_ai
            self.set_ai_response(readable_ai_response)

            # TODO : tester la langue, si elle n'est pas français,
            # traduir automatiquement en français
            entree2.tag_configure(
                tagName="boldtext", font=entree2.cget("font") + " bold"
            )
            entree2.tag_configure(
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
            entree2.tag_configure(
                "balise",
                font=(entree2.cget("font") + " italic", 8),
                foreground=_from_rgb((100, 100, 100)),
            )
            entree2.tag_configure(
                "balise_bold",
                font=(entree2.cget("font") + " bold", 8),
                foreground=_from_rgb((100, 100, 100)),
            )
            entree2.insert(
                tk.END,
                datetime.datetime.now().isoformat() + " <" + self.get_model() + ">\n",
                "balise",
            )
            entree2.insert(
                tk.END,
                str(_timing) + "millisecondes < " + str(type(agent_appel)) + " >\n",
                "balise_bold",
            )
            # entree2.insert(tk.END, readable_ai_response, "response")
            entree2.insert_markdown(readable_ai_response + "\n\n")
            # entree2.insert(tk.END, "\n\n" + "</" + self.get_model() + ">\n\n", "balise")

            entree2.update()
            return readable_ai_response

        def save_to_submission() -> bool:
            # Afficher une boîte de message de confirmation
            speciality = motcles_widget.get()
            if len(speciality) <= 1:
                speciality = ""

            try:
                selection = entree1.get(tk.SEL_FIRST, tk.SEL_LAST)
            except:
                selection = entree1.get("1.0", tk.END)
            finally:
                if len(selection) > 1:
                    self.set_submission(
                        content=self.get_submission() + "\n" + selection + "\n"
                    )
                    return True
                elif len(self.get_submission().lower()) > 1:
                    return True
                else:
                    return False

        def quitter(self) -> str:
            # Afficher une boîte de message de confirmation
            if messagebox.askyesno(
                "Confirmation", "Êtes-vous sûr de vouloir quitter ?"
            ):
                save_to_submission()
                self.destroy()
            else:
                print("L'utilisateur a annulé.")

        def lire_text_from_object(object: tk.Text):
            texte_to_talk = object.get("1.0", tk.END)

            if texte_to_talk != "":
                try:
                    texte_to_talk = object.get(tk.SEL_FIRST, tk.SEL_LAST)
                except:
                    texte_to_talk = object.get("1.0", tk.END)
                finally:
                    self.talker(texte_to_talk, False)

        def clear_entree1():
            entree1.replace("1.0", tk.END, "")

        def clear_entree2():
            entree2.replace("1.0", tk.END, "")

        def load_txt():
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
                self.talker("Fin de l'extraction", False)

                # on prepare le text pour le présenter à la méthode insert_markdown
                # qui demande un texte fait de lignes séparées par des \n
                # transforme list[str] -> str
                resultat_reformater = "".join(resultat_txt)
                entree1.insert_markdown(mkd_text=resultat_reformater)

            except:
                messagebox("Problème avec ce fichier txt")

        def load_pdf():
            try:
                file_to_read = filedialog.askopenfile(
                    parent=self,
                    title="Ouvrir un fichier pdf",
                    defaultextension="pdf",
                    mode="r",
                    initialdir=".",
                )
                self.talker("Extraction du PDF", False)
                resultat_txt = read_pdf(file_to_read.name)
                self.talker("Fin de l'extraction", False)
                entree1.insert_markdown(mkd_text=resultat_txt)
            except:
                messagebox("Problème avec ce fichier pdf")

        def textwidget_to_mp3(object: tk.Text):
            texte_to_save_to_mp3 = object.get("1.0", tk.END)

            if texte_to_save_to_mp3 != "":
                try:
                    texte_to_save_to_mp3 = object.get(tk.SEL_FIRST, tk.SEL_LAST)
                except:
                    texte_to_save_to_mp3 = object.get("1.0", tk.END)
                finally:
                    self.talker("transcription du texte vers un fichier mp3", False)
                    simple_dialog = simpledialog.askstring(
                        parent=self,
                        prompt="Enregistrement : veuillez choisir un nom au fichier",
                        title="Enregistrer vers audio",
                    )
                    lecteur.save_to_file(
                        texte_to_save_to_mp3, simple_dialog.lower() + ".mp3"
                    )
                    self.talker("terminé", False)
            else:
                self.talker("Désolé, Il n'y a pas de texte à enregistrer en mp3", False)

        def refresh_entree_html(texte: str, ponctuel: bool = True):
            markdown_content = markdown.markdown(texte, output_format="xhtml")
            html_entries = entree2.get("1.0", tk.END)
            if ponctuel:
                html_entries += (
                    "<strong style='color:grey;'>Question:</strong>"
                    + '<span style="font-size: 12;color:grey;text-align:justify">'
                    + self.get_submission()
                    + "</span>"
                    + "<strong style='color:red;'>Réponse:</strong>"
                    + '<span style="font-size: 12;color:brown;text-align:justify">'
                    + markdown_content
                    + "</span>"
                    + "</span>"
                )
            else:
                html_entries += markdown_content

            # entree2.set_html(html_entries)
            entree2.update()

        def replace_in_place(
            texte: str, index1: str, index2: str, ponctuel: bool = True
        ):
            entree1.replace(chars=texte, index1=index1, index2=index2)

        def translate_inplace():
            traduit_maintenant()

        def traduit_maintenant():
            was_a_list = False
            try:
                texte_initial = entree1.get(tk.SEL_FIRST, tk.SEL_LAST)
                indx1 = entree1.index(tk.SEL_FIRST)
                indx2 = entree1.index(tk.SEL_LAST)

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
                texte_initial = entree1.get("1.0", tk.END)
                texte_traite = traitement_du_texte(texte_initial, 500)
                if isinstance(texte_traite, list):
                    for element in texte_traite:
                        translated_text = str(translate_it(text_to_translate=element))
                        refresh_entree_html(translated_text, False)
                    was_a_list = True
                elif was_a_list == True:
                    translated_text = str(translate_it(text_to_translate=texte_traite))
                    refresh_entree_html(translated_text, False)
                else:
                    translated_text = str(translate_it(text_to_translate=texte_traite))
                    refresh_entree_html(translated_text, True)
                self.talker("fin de la traduction", False)

        affiche_illustration(
            self,
            image=image,
            quitter=lambda: quitter(self=root),
            message="... Jonathan LivingStone, dit legoeland",
            fenetre=self,
        )

        button_frame = tk.Frame(self, relief="sunken", name="button_frame")
        button_frame.configure(background=_from_rgb(DARK0))
        button_frame.pack(fill="x", expand=True)
        canvas_edition = tk.Frame(self, relief="sunken")

        canvas1 = tk.Frame(canvas_edition, relief="sunken")
        boutons_effacer_canvas2 = tk.Frame(canvas_edition)
        canvas2 = tk.Frame(canvas_edition, relief="sunken")

        canvas_edition.pack(fill="x", expand=True)
        canvas1.pack(fill="x", expand=True)
        boutons_effacer_canvas2.pack(fill="x", expand=True)
        canvas2.pack(fill="x", expand=True)

        # entree1 = tk.Text(canvas1, name="entree1")
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=8)
        entree1 = SimpleMarkdownText(canvas1, height=20, font=default_font)

        # Attention la taille de la police, ici 10, ce parametre
        # tant à changer le cadre d'ouverture de la fenetre
        entree1.configure(
            bg=_from_rgb((200, 200, 200)),
            fg=_from_rgb((60, 60, 60)),
            font=("arial", 10),
            wrap="word",
            padx=10,
            pady=6,
            height=15,
        )
        boutton_effacer_entree1 = tk.Button(
            button_frame, text="x", command=clear_entree1
        )
        boutton_effacer_entree1.configure(bg="red", fg="white")
        boutton_effacer_entree1.pack(side="right")
        scrollbar1 = tk.Scrollbar(canvas1)
        scrollbar1.pack(side=tk.RIGHT, fill="both")
        entree1.tag_configure("italic", font=entree1.cget("font") + " italic")
        entree1.insert_markdown(
            mkd_text=msg_to_write + " **< CTRL + RETURN > pour valider.**"
        )
        entree1.focus_set()
        entree1.pack(fill="both", expand=True)
        entree1.configure(yscrollcommand=scrollbar1.set)
        entree1.bind("<Control-Return>", func=go_submit)

        # Création d'un champ de saisie de l'utilisateur
        boutton_effacer_entree2 = tk.Button(
            boutons_effacer_canvas2, text="x", command=clear_entree2
        )

        boutton_effacer_entree2.configure(bg="red", fg="white")
        boutton_effacer_entree2.pack(side="right")
        bouton_lire2 = tk.Button(
            boutons_effacer_canvas2,
            text="Lire",
            command=lambda: lire_text_from_object(entree2),
        )
        bouton_lire2.configure(bg="green", fg="white")
        bouton_lire2.pack(side=tk.RIGHT)
        bouton_transfere = tk.Button(
            boutons_effacer_canvas2,
            text="Transférer",
            command=lambda: entree1.insert_markdown(self.get_ai_response()),
        )
        bouton_transfere.pack(side=tk.RIGHT, fill="both")
        scrollbar2 = tk.Scrollbar(canvas2)
        scrollbar2.pack(side=tk.RIGHT, fill="both")
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=8)
        entree2 = SimpleMarkdownText(canvas2, height=20, font=default_font)
        entree2.configure(
            bg="white",
            fg="black",
            font=("arial ", 12),
            height=15,
            wrap="word",
            padx=10,
            pady=6,
            yscrollcommand=scrollbar2.set,
        )
        entree2.pack(fill="both", expand=True)

        scrollbar2.configure(command=entree2.yview, bg=_from_rgb(DARK0))
        scrollbar1.configure(command=entree1.yview, bg=_from_rgb(DARK0))

        # Création d'un bouton pour Lire
        bouton_lire1 = tk.Button(
            button_frame, text="Lire", command=lambda: lire_text_from_object(entree1)
        )
        bouton_lire1.configure(
            bg=_from_rgb((0, 0, 0)),
            fg="white",
            highlightbackground="red",
            highlightcolor="white",
            activebackground="red",
        )
        bouton_lire1.pack(side=tk.LEFT)

        # Création d'un bouton pour traduction_sur_place
        bouton_traduire_sur_place = tk.Button(
            button_frame, text="Traduire", command=translate_inplace
        )
        bouton_traduire_sur_place.configure(
            bg=_from_rgb((40, 40, 40)),
            fg="white",
            highlightbackground="red",
            highlightcolor="white",
        )
        bouton_traduire_sur_place.pack(side=tk.LEFT)

        # Création d'un bouton pour Dicter
        bouton_commencer_diction = tk.Button(
            button_frame, text=" ф ", command=lance_ecoute
        )
        bouton_commencer_diction.configure(bg="red", fg="white")

        bouton_commencer_diction.pack(side=tk.LEFT)

        # Création d'un bouton pour soumetre
        bouton_soumetre = tk.Button(button_frame, text="Ask to AI", command=soumettre)
        bouton_soumetre.configure(
            bg=_from_rgb((120, 120, 120)),
            fg="white",
            highlightbackground="red",
            highlightcolor="white",
        )
        bouton_soumetre.pack(side=tk.LEFT)

        bouton_save_to_mp3 = tk.Button(
            button_frame,
            text="texte vers mp3",
            command=lambda: textwidget_to_mp3(entree1),
        )
        bouton_save_to_mp3.configure(bg=_from_rgb((160, 160, 160)), fg="black")
        bouton_save_to_mp3.pack(side="left")

        bouton_load_pdf = tk.Button(button_frame, text="Charger Pdf", command=load_pdf)
        bouton_load_pdf.configure(bg=_from_rgb((160, 160, 160)), fg="black")
        bouton_load_pdf.pack(side="left")

        bouton_load_txt = tk.Button(button_frame, text="Charger TXT", command=load_txt)
        bouton_load_txt.configure(bg=_from_rgb((160, 160, 160)), fg="black")
        bouton_load_txt.pack(side="left")

        motcles_widget = tk.Entry(
            button_frame,
            name="motcles_widget",
            width=30,
            fg="red",
            bg="black",
            font=("trebuchet", 10, "bold"),
            relief="flat",
        )
        button_keywords = tk.Button(
            button_frame,
            text="Mot-clé",
            background=_from_rgb(DARK0),
            foreground="white",
            command=lambda: affiche_prepromts(PROMPTS_SYSTEMIQUES.keys()),
        )
        button_keywords.pack(side=tk.RIGHT, expand=False)
        motcles_widget.pack(side="left", padx=2, pady=2)

        # TODO NE fonctionne pas pour mettre en pause la lecture à haute voix
        # bouton_stop=tk.Button(button_frame,text="Stop",command=lecteur.endLoop)
        # bouton_reprendre=tk.Button(button_frame,text="reprendre",command=lecteur.startLoop)
        # bouton_stop.pack(side=tk.LEFT)
        # bouton_reprendre.pack(side=tk.LEFT)


def traitement_du_texte(texte: str, number: int) -> list[list[str]]:
    """
    ### traitement_du_texte
    #### si le texte possède plus de <number> caractères :
        on coupe le texte en plusieurs listes de maximum <number> caractères
        et on renvois cette liste de liste
    #### sinon :
        on envois le texte telquel

    ### RETURN : str ou List
    """
    # on découpe le texte par mots
    liste_of_words = texte.split()
    if len(liste_of_words) >= number:
        list_of_large_text: list[list[str]] = []
        new_list: list[str] = []
        counter = 0
        for word in liste_of_words:
            counter += len(word) + 1
            new_list.append(word)
            if counter >= number:
                list_of_large_text.append(new_list)
                new_list = []
                counter = 0
        return list_of_large_text
    else:
        return texte


def affiche_ia_list(list_to_check: list):
    """
    Display a list of AI you can use
    * affiche la listebox avec la liste donnée en paramètre list_to_check
    * click on it cause model AI to change
    """
    _listbox: tk.Listbox = traite_listbox(list_to_check)
    _listbox.bind("<<ListboxSelect>>", func=change_model_ia)


def affiche_prepromts(list_to_check: list):
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
    app.set_motcle(mots_cle.split())

    # on récupère le tk.Entry de la fenetre principale : button_frame.motcles_widget
    # on le clean et on y insère le thème récupéré par la simpledialog auparavant
    _speciality_widget: tk.Entry = app.nametowidget("button_frame.motcles_widget")
    _speciality_widget.select_range("1.0", tk.END)
    _speciality_widget.selection_clear()
    _speciality_widget.insert(0, mots_cle)

    # crée et affiche une _listbox remplie avec la variable list_to_check
    _listbox: tk.Listbox = traite_listbox(list_to_check)

    # bind sur l'événement sélection d'un item de la liste
    # vers la fonction charge_preprompt
    _listbox.bind("<<ListboxSelect>>", func=charge_preprompt)


def traite_listbox(list_to_check: list):
    frame = tk.Tk(className="list_ia")
    frame.grid_location(root.winfo_x() + 50, root.winfo_y() + 30)
    _list_box = tk.Listbox(frame)
    scrollbar_listbox = tk.Scrollbar(frame)
    scrollbar_listbox.configure(command=_list_box.yview)

    _list_box.pack(side=tk.LEFT, fill="both")
    for item in list_to_check:
        _list_box.insert(tk.END, item)
    _list_box.configure(
        background="red",
        foreground="black",
        yscrollcommand=scrollbar_listbox.set,
    )
    scrollbar_listbox.pack(side=tk.RIGHT, fill="both")

    return _list_box


def maximize(object: SimpleMarkdownText):
    object.configure(height=11)


def minimize(object: SimpleMarkdownText):
    object.destroy()


def charge_preprompt(evt: tk.Event):
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
            prompt_name=str(app.get_motcle()).lower(),
        )
        app.set_submission(preprompt)

        app.get_talker()("prépromt ajouté : " + preprompt, False)

    except:
        print("aucun préprompt sélectionné")
        app.get_talker()("Oups", False)
    finally:
        w.focus_get().destroy()


def clean_infos_model(button: tk.Button, text_area: SimpleMarkdownText):
    button.destroy()
    text_area.destroy()


def display_infos_model(master: tk.Canvas, content: Mapping[str, Any]):
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=8)
    canvas_bouton_minimize = tk.Canvas(master=master, bg="black")
    canvas_bouton_minimize.pack(fill="x", expand=True)
    infos_model = SimpleMarkdownText(master, font=default_font)
    bouton_minimize = tk.Button(
        canvas_bouton_minimize,
        text="-",
        command=lambda: clean_infos_model(
            button=canvas_bouton_minimize, text_area=infos_model
        ),
        fg="black",
        bg="red",
    )
    bouton_minimize.pack(side=tk.RIGHT)
    infos_model.configure(background="black", fg="white", height=11)
    print("okok")
    jsonified = (
        json.dumps(
            content["details"],
            indent=4,
        )
        + "\n"
    )

    print(jsonified)
    infos_model.pack(fill="x", expand=True)
    infos_model.insert_markdown(mkd_text=jsonified)


def change_model_ia(evt: tk.Event):
    # Note here that Tkinter passes an event object to onselect()
    w: tk.Listbox = evt.widget
    try:
        index = w.curselection()[0]
        value = w.get(index)
        print('You selected item %d: "%s"' % (index, value))
        app.set_model(name_ia=str(value))
        _widget: tk.Button = app.nametowidget("cnvs1.cnvs2.btnlist")
        _widget.configure(text=value)
        model_info = ollama.show(app.get_model())
        app.get_talker()("ok", False)
        display_infos_model(master=app.nametowidget("cnvs1"), content=model_info)
    except:
        print("aucune ia sélectionner")
        app.get_talker()("Oups", False)
    finally:
        w.focus_get().destroy()


def affiche_illustration(
    self: Fenetre_entree, image: ImageTk, fenetre, message, quitter
):
    """affiche l'illustration du goeland ainsi que son slogan"""
    # ## PRESENTATION DU GOELAND  ####
    cnvs1 = tk.Frame(fenetre, background=_from_rgb(DARK0), name="cnvs1")
    # cnvs1.configure(bg=_from_rgb((69, 122, 188)))
    cnvs1.pack(fill="x", expand=True)
    # ################################
    cnvs2 = tk.Frame(cnvs1, name="cnvs2")
    cnvs2.configure(bg="black")
    cnvs2.pack(fill="x", expand=False)

    # Create a canvas
    canva = tk.Canvas(
        cnvs1,
        height=BANNIERE_HEIGHT,
        width=BANNIERE_WIDTH,
        background=_from_rgb(DARK0),
        name="canva",
    )

    # Création d'un bouton pour quitter
    bouton_quitter = tk.Button(cnvs2, text="Quitter", command=quitter)
    bouton_quitter.configure(background=_from_rgb(DARK0), foreground="red")
    bouton_quitter.pack(side=tk.LEFT)

    bouton_Ola = tk.Button(
        cnvs2,
        text="Ola",
        command=lambda: self.set_client(Ola),
        highlightthickness=3,
        highlightcolor="yellow",
    )
    bouton_Ola.configure(background=_from_rgb(DARK0), foreground="red")
    bouton_Ola.pack(side=tk.LEFT)

    bouton_Ollama = tk.Button(
        cnvs2,
        text="Ollama",
        command=lambda: self.set_client(ollama.Client(host="http://127.0.0.1:11434")),
        highlightthickness=3,
        highlightcolor="yellow",
    )
    bouton_Ollama.configure(background=_from_rgb(DARK0), foreground="red")
    bouton_Ollama.pack(side=tk.LEFT)

    bouton_liste = tk.Button(
        cnvs2,
        name="btnlist",
        text="Changer d'IA",
        background="red",
        foreground="black",
        command=lambda: affiche_ia_list(my_liste),
    )

    label = tk.Label(
        cnvs2,
        text=message,
        font=("Trebuchet", 8),
        fg="white",
        bg=_from_rgb(DARK0),
    )

    label.pack(side=tk.RIGHT, expand=False)
    bouton_liste.pack(side=tk.RIGHT, expand=False)

    # Add the image to the canvas, anchored at the top-left (northwest) corner
    canva.create_image(0, 0, anchor="nw", image=image, tags="bg_img")
    canva.pack(fill="x", expand=True)


def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    You must give a tuplet (r,g,b) like _from_rgb((125,125,125))"""
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


async def dire_tt(alire: str):
    lecteur.say(alire)
    lecteur.runAndWait()

    # lecteur.endLoop()
    return lecteur.stop()


# TODO : loop async for saytt
def start_loop_saying(texte: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(loop.create_task(dire_tt(alire=texte)))


def say_tt(alire: str):
    the_thread = threading.Thread(target=start_loop_saying(texte=alire))
    the_thread.start()


def say_txt(alire: str, stop_ecoute: bool):
    if not STOP_TALKING:
        if stop_ecoute:
            arret_ecoute()
        lecteur.say(alire)
        lecteur.runAndWait()
        lecteur.stop()


def arret_ecoute():
    stream.stop_stream()


def debut_ecoute(info: str = ""):
    say_txt(info, False)
    stream.start_stream()
    return 0, ""


def read_prompt_file(file):
    with open(file, "r", encoding="utf-8") as file_to_read:
        content = file_to_read.readlines()
    return content


def changer_ia(self, evt):
    # Note here that Tkinter passes an event object to onselect()
    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    print('You selected item %d: "%s"' % (index, value))
    self.set_model(value)


def translate_it(text_to_translate: str) -> str:
    """
    traduit le text reçu par maximum de 500 caractères. Si le text est une liste, on la traduit une à une str
    @param text: desired text to translate, maximum de 500 caractères
    @return: str: translated text
    """

    # Use any translator you like, in this example GoogleTranslator
    from deep_translator import GoogleTranslator as _translator

    if not isinstance(text_to_translate, str):
        reformat_translated = " ".join(str(x) for x in text_to_translate)
    else:
        reformat_translated = text_to_translate

    translated = _translator(source="auto", target="fr").translate(
        text=reformat_translated
    )  # output -> Weiter so, du bist großartig

    # print(translated)
    return translated


def actualise_index_html(texte: str, question: str):
    if len(question) > 500:
        question = question[:499] + "..."
    with open("index" + ".html", "a", encoding="utf-8") as file_to_update:
        markdown_response = markdown.markdown(texte, output_format="xhtml")
        markdown_question = markdown.markdown(question, output_format="xhtml")
        file_to_update.write(
            "<div id='response_ai'>"
            + "<div id=question_to_ai>"
            + "<h3>Prompt</h3>"
            + markdown_question
            + "\n"
            + "</div>"
            + markdown_response
            + "\n"
            + "</div>"
        )


def main(prompt=False, stop_talking=STOP_TALKING):
    """Début du programme principal"""
    if prompt:
        model_used = init_model(LLAMA3, prompted=True)
        return traitement_rapide(
            prompt,
            model_to_use=model_used,
            talking=stop_talking,
            moteur_diction=say_tt,
        )

    model_used = init_model(LLAMA3, prompted=False)
    say_txt("IA initialisée ! ", stop_ecoute=False)
    print(
        "ZicChatbotAudio\n"
        + STARS * WIDTH_TERM
        + "\nChargement... Veuillez patienter\n"
        + STARS * WIDTH_TERM
    )

    # prend beaucoup de temp
    # passer ça en asynchrone
    model_ecouteur_micro = engine_ecouteur_init()

    say_txt("micro audio initialisé", False)

    # Create a recognizer
    rec = vosk.KaldiRecognizer(model_ecouteur_micro, 16000)
    say_txt("reconnaissance vocale initialisée", False)

    # root = tk.Tk()
    root.title = "RootTitle - "
    root.resizable(False, False)
    root.geometry(str(FENETRE_WIDTH) + "x" + str(FENETRE_HEIGHT))

    app.title = "MyApp"

    app.set_talker(say_txt)
    app.set_engine(rec)
    app.mainloop()


def init_main():
    # Open the microphone stream
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=8192,
    )

    my_liste = []
    for element in (ollama.list())["models"]:
        my_liste.append(element["name"])

    print(my_liste)
    return my_liste, stream


def init_start(engine_lecteur_init, init_main):
    my_liste, stream = init_main()

    lecteur = engine_lecteur_init()
    return lecteur, my_liste, stream


# Début du programme
lecteur, my_liste, stream = init_start(engine_lecteur_init, init_main)

root = tk.Tk(className="YourAssistant")
app = Fenetre_entree(
    master=root,
    stream=stream,
    model_to_use=LLAMA3,
)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create a ArcHydro schema")
    parser.add_argument(
        "--prompt", metavar="prompt", required=False, help="the prompt to ask"
    )
    parser.add_argument(
        "--talk", metavar="talk", required=False, help="set talking to on"
    )
    args: Namespace = parser.parse_args()

    main(prompt=args.prompt, stop_talking=args.talk)
