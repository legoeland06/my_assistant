# zic_chat.py
from argparse import Namespace
import asyncio
import time
import tkinter as tk

# from tkinter import simpledialog
from tkinter import messagebox
import vosk
import pyaudio
import ollama
from groq import Groq
from llama_index.llms.ollama import Ollama as Ola
from FenetrePrincipale import FenetrePrincipale
from StoppableThread import StoppableThread
from Constants import *
from outils import (
    actualise_index_html,
    append_response_to_file,
    engine_lecteur_init,
    say_txt,
)


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
    say_txt("initialisation du moteur de reconnaissance vocale ")
    model_ecouteur_micro = engine_ecouteur_init()
    say_txt("reconnaissance vocale initialisée")

    # Create a recognizer
    say_txt("initialisation du micro")
    rec = vosk.KaldiRecognizer(model_ecouteur_micro, 16000)
    say_txt("micro initialisé")

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
