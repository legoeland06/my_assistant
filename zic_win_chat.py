# zic_chat.py
from argparse import Namespace
import asyncio
import time
import tkinter as tk

# from tkinter import simpledialog
from tkinter import messagebox
from groq import Groq
import openai
import vosk
import pyaudio
import ollama
from llama_index.llms.ollama import Ollama as Ola
from FenetrePrincipale import FenetrePrincipale
from StoppableThread import StoppableThread
import Constants as cst
from outils import (
    actualise_index_html,
    append_response_to_file,
    engine_lecteur_init,
    say_txt,
)
from secret import GROQ_API_KEY


def engine_ecouteur_init():
    # set verbosity of vosk to NO-VERBOSE
    vosk.SetLogLevel(-1)
    # Initialize the model and return an instance
    try:
        model = vosk.Model(cst.MODEL_PATH, lang="fr-fr")
        return model
    except:
        raise Exception("Pas de model de reconaissance vocale chargé")


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

    print("PROMPT:: \n" + prompt)
    mytime = time.perf_counter_ns()
    ai_response=""
    if isinstance(agent_appel, Groq):

        this_message = [
            {
                "role": "system",
                "content": "",
            },
            {
                "role": "assistant",
                "content": "",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        try:
            llm: openai.ChatCompletion = agent_appel.chat.completions.create(
                messages=this_message,
                model=model_to_use,
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )

            ai_response = llm.choices[0].message.content
            print(str(type(ai_response)))

        except:
            messagebox.Message("OOps, ")

    # calcul le temps écoulé par la thread
    timing: float = (time.perf_counter_ns() - mytime) / 1_000_000_000.0

    # TODO
    print(ai_response)

    return ai_response, timing


def traitement_rapide(texte: str, model_to_use,talking):
    groq_client = Groq(api_key=GROQ_API_KEY)

    ai_response, _timing = ask_to_ai(
        agent_appel=groq_client, prompt=texte, model_to_use=model_to_use
    )
    readable_ai_response = ai_response
    say_txt(readable_ai_response) if talking else None


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
    # the_thread.join()
    the_thread.stop()


def main(prompt=False):
    """Début du programme principal"""
    # thread_name=the_thread.name
    if prompt:
        model_used = "llama3-70b-8192"
        traitement_rapide(
            prompt,
            model_to_use=model_used,
            talking=False
        )
        exit(0)

    model_used = init_model(cst.LLAMA3, prompted=False)
    app.say_txt("IA initialisée ! ")
    print(
        "ZicChatbotAudio\n"
        + cst.STARS * cst.WIDTH_TERM
        + "\nChargement... Veuillez patienter\n"
        + cst.STARS * cst.WIDTH_TERM
    )

    # prend beaucoup de temp
    # passer ça en asynchrone
    app.say_txt("chargement du moteur de reconnaissance vocale ")
    model_ecouteur_micro = engine_ecouteur_init()
    app.say_txt("reconnaissance vocale initialisée")

    # Create a recognizer
    app.say_txt("initialisation du micro")
    rec = vosk.KaldiRecognizer(model_ecouteur_micro, 16000)
    app.say_txt("micro initialisé")

    root.title = "RootTitle - "

    app.title = "MyApp"

    the_thread = StoppableThread()
    app.set_thread(the_thread)
    app.set_talker(talker=say_txt)
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
    model_to_use=cst.LLAMA3,
)
# sisi.mainloop(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create a ArcHydro schema")
    parser.add_argument(
        "--prompt", metavar="prompt", required=False, help="the prompt to ask"
    )
    
    args: Namespace = parser.parse_args()

    main(prompt=args.prompt)
