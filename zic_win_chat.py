# zic_chat.py
from argparse import Namespace
import asyncio
import datetime
import json.tool
import re
import threading
import time
import tkinter as tk

# from tkinter import simpledialog
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import filedialog
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
from FenetrePrincipale import FenetrePrincipale
from FenetreScrollable import FenetreScrollable
from SimpleMarkdownText import SimpleMarkdownText
from StoppableThread import StoppableThread
from FenetreResponse import FenetreResponse
from Constants import *
from outils import (
    actualise_index_html,
    append_response_to_file,
    engine_lecteur_init,
    from_rgb_to_tkColors,
    bold_it,
    lire_text_from_object,
    load_txt,
    read_pdf,
    say_txt,
    traitement_du_texte,
    translate_it,
)


def affiche_preprompts():
    print(INFOS_PROMPTS)
    print(STARS * WIDTH_TERM)
    for preprompt in PREPROMPTS:
        print(str(PREPROMPTS.index(preprompt)) + ". " + preprompt)


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


def ask_to_ai(agent_appel, prompt, model_to_use):

    app.set_timer(time.perf_counter_ns())

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
    timing: float = (time.perf_counter_ns() - app.get_timer()) / 1_000_000_000.0
    print(ai_response)
    print("Type_agent_appel::" + str(type(agent_appel)))
    print("Type_ai_réponse::" + str(type(ai_response)))

    append_response_to_file(RESUME_WEB, ai_response)
    actualise_index_html(
        texte=ai_response, question=prompt, timing=timing, model=model_to_use
    )

    return ai_response, timing


def traitement_rapide(texte: str, model_to_use, talking: bool, moteur_diction):
    ai_response, _timing = ask_to_ai(
        agent_appel=ollama.Client, prompt=texte, model_to_use=model_to_use
    )
    readable_ai_response = ai_response
    app.get_talker()(readable_ai_response)


def maximize(object: SimpleMarkdownText):
    object.configure(height=11)


def minimize(object: SimpleMarkdownText):
    object.destroy()


async def dire_tt(alire: str):
    if lecteur.isBusy():
        lecteur.stop()

    if lecteur._inLoop:
        lecteur.endLoop()

    lecteur.say(alire)
    lecteur.runAndWait()


# TODO : loop async for saytt
def start_loop_saying(texte: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(loop.create_task(dire_tt(alire=texte)))


def say_tt(alire: str):
    """
    lit le texte en passant par un thread.
    ne bloque pas l'execution du programme
    """

    the_thread = app.get_thread()
    print("<SAYTT>récupéré : " + "ok" if the_thread.name else "pasok")
    if not the_thread.stopped():
        print("<SAYTT> à stopper : " + the_thread.name)
        the_thread.stop()
    else:
        print("<SAYTT> inutile à stopper : " + the_thread.name)

    the_thread = StoppableThread(None, target=start_loop_saying(alire))
    print("</SAYTT> nouvelle thread started: " + the_thread.name)
    app.set_thread(the_thread)
    the_thread.start()

    # TODO : intégrer ici un moyen de controle de la diction
    # bouton lecture, stop, pause, effacer
    the_thread.join()
    the_thread.stop()


def arret_ecoute():
    stream.stop_stream()


def debut_ecoute(info: str = ""):
    say_txt(info, False)
    stream.start_stream()
    return 0, ""


def changer_ia(self, evt):
    # Note here that Tkinter passes an event object to onselect()
    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    print('You selected item %d: "%s"' % (index, value))
    self.set_model(value)


def main(prompt=False, stop_talking=STOP_TALKING):
    """Début du programme principal"""
    # thread_name=the_thread.name
    if prompt:
        model_used = init_model(LLAMA3, prompted=True)
        return traitement_rapide(
            prompt,
            model_to_use=model_used,
            talking=stop_talking,
            moteur_diction=say_tt,
        )

    model_used = init_model(LLAMA3, prompted=False)
    say_txt("IA initialisée ! ")
    print(
        "ZicChatbotAudio\n"
        + STARS * WIDTH_TERM
        + "\nChargement... Veuillez patienter\n"
        + STARS * WIDTH_TERM
    )

    # prend beaucoup de temp
    # passer ça en asynchrone
    model_ecouteur_micro = engine_ecouteur_init()

    say_txt("micro audio initialisé")

    # Create a recognizer
    rec = vosk.KaldiRecognizer(model_ecouteur_micro, 16000)
    say_txt("reconnaissance vocale initialisée")

    root.title = "RootTitle - "

    app.title = "MyApp"

    the_thread = StoppableThread()
    app.set_thread(the_thread)
    app.set_talker(say_tt)
    app.set_engine(rec)
    app.mainloop(0)


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

    return stream


def init_start(engine_lecteur_init, init_main):
    stream = init_main()

    lecteur = engine_lecteur_init()
    return lecteur, stream


# Début du programme
lecteur, stream = init_start(engine_lecteur_init, init_main)

root = tk.Tk(className="YourAssistant")


app = FenetrePrincipale(
    master=root,
    stream=stream,
    model_to_use=LLAMA3,
)
# sisi.mainloop(1)


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
