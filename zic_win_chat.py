# zic_chat.py
from argparse import Namespace
import time
import tkinter as tk

# from tkinter import simpledialog
from tkinter import messagebox
from groq import Groq
import openai
import vosk
import pyaudio
from FenetrePrincipale import FenetrePrincipale
import Constants as cst
from outils import engine_lecteur_init, lancement_de_la_lecture, say_txt
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


def init_model(model_to_use: str):
    """
    initialise le model à utiliser avant d'envoyer un prompt
    """
    msg = (
        "Chargement de l'Ia : ["
        + (
            model_to_use[: model_to_use.find(":")]
            if model_to_use.find(":") != -1
            else model_to_use
        )
        + "]... Un instant"
    )
    print(msg)

    lecteur.say(msg)
    lecteur.runAndWait()
    lecteur.stop()
    return model_to_use


def ask_to_ai(agent_appel, prompt, model_to_use):

    print("PROMPT:: \n" + prompt)
    mytime = time.perf_counter_ns()
    ai_response = ""
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


def traitement_rapide(texte: str, model_to_use, talking) -> str:
    groq_client = Groq(api_key=GROQ_API_KEY)

    ai_response, _timing = ask_to_ai(
        agent_appel=groq_client, prompt=texte, model_to_use=model_to_use
    )
    readable_ai_response = ai_response
    lancement_de_la_lecture(readable_ai_response) if talking else None
    return readable_ai_response


def main(prompt=False):
    """
    ## begining of the application
    if prompt is True, the application still in terminal
    and responses were returned and printed in the terminal
    and exit programme
    """
    if prompt:
        model_used = cst.LLAMA370B
        traitement_rapide(prompt, model_to_use=model_used, talking=False)
        exit(0)

    model_used = cst.LLAMA370B.split(":")[0]
    lancement_de_la_lecture("Ia séléctionnée :"+model_used)
    print(
        "ZicChatbotAudio\n"
        + cst.STARS * cst.WIDTH_TERM
        + "\nChargement... Veuillez patienter\n"
        + cst.STARS * cst.WIDTH_TERM
    )

    lancement_de_la_lecture("chargement du moteur de reconnaissance vocale ")
    model_ecouteur_micro = engine_ecouteur_init()
    lancement_de_la_lecture("reconnaissance vocale initialisée")

    # initialise a voice recognizer
    lancement_de_la_lecture("initialisation du micro")
    rec = vosk.KaldiRecognizer(model_ecouteur_micro, 16000)
    lancement_de_la_lecture("micro initialisé")

    root.title = "RootTitle - "

    app.title = "MyApp"

    app.set_engine(rec)

    # Mode de développement
    # BYPASS les sélection IHM chronophages en mode dev
    groq_client = Groq(api_key=GROQ_API_KEY)
    app.set_client(groq_client)
    app.set_model(cst.LLAMA370B)
    app.bouton_commencer_diction.invoke()
    # après cette invocation l'application est lancée en mode audioChat directement

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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create a ArcHydro schema")
    parser.add_argument(
        "--prompt", metavar="prompt", required=False, help="the prompt to ask"
    )

    args: Namespace = parser.parse_args()

    main(prompt=args.prompt)
