# zic_chat.py
from argparse import Namespace
import time
import tkinter as tk

from tkinter import messagebox
from groq import Groq
import openai
import vosk
import pyaudio
from FenetrePrincipale import FenetrePrincipale
import Constants as cst
from outils import askToAi, thread_lecture
from secret import GROQ_API_KEY


def init_model_vocal():
    # set verbosity of vosk to NO-VERBOSE
    vosk.SetLogLevel(-1)
    # Initialize the model and return an instance
    try:
        model = vosk.Model(cst.MODEL_PATH, lang="fr-fr")
        return model
    except:
        raise Exception("Pas de model de reconaissance vocale chargé")


def ask_to_ai(agent_appel, prompt, model_to_use):

    print("PROMPT:: \n" + prompt)
    mytime = time.perf_counter_ns()
    ai_response = ""
    if isinstance(agent_appel, Groq):

        this_message = [
            {
                "role": cst.ROLE_SYSTEM,
                "content": "",
            },
            {
                "role": cst.ROLE_ASSISTANT,
                "content": "",
            },
            {
                "role": cst.ROLE_USER,
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
    thread_lecture(readable_ai_response) if talking else None
    return readable_ai_response


def init_main():
    # Open the microphone stream
    p = pyaudio.PyAudio()
    return p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=8192,
    )


def main(prompt=False):
    """
    ## begining of the application
    if prompt is True, the application still in terminal
    and responses were returned and printed in the terminal
    and exit programme
    """
    model_used = cst.LLAMA370B.split(":")[0]

    # utilisation en mode terminal avec l'option --prompt
    if prompt:
        # model_used = cst.LLAMA370B
        print(askToAi(prompt, model_to_use=model_used))
        exit(0)

    # Début du programme en mode fenetre
    root = tk.Tk(className="YourAssistant")
    root.title = "RootTitle - "
    app = FenetrePrincipale(
        master=root,
        stream=init_main(),
        model_to_use=model_used,
    )
    app.title = "MyApp"
    # initialise a voice recognizer
    thread_lecture("chargement du moteur de reconnaissance vocale ")
    model_vocal = init_model_vocal()
    thread_lecture("reconnaissance vocale initialisée")
    thread_lecture("ouverture du micro")
    rec = vosk.KaldiRecognizer(model_vocal, 16000)
    thread_lecture("micro ouvert")
    app.set_engine(rec)

    thread_lecture("Ia sélectionnée :" + model_used)
    print(
        "ZicChatbotAudio\n"
        + cst.STARS * cst.WIDTH_TERM
        + "\nChargement... Veuillez patienter\n"
        + cst.STARS * cst.WIDTH_TERM
    )

    # Mode de développement
    # BYPASS les sélection IHM chronophages en mode dev
    groq_client = Groq(api_key=GROQ_API_KEY)
    time.sleep(2)
    app.set_client(groq_client)
    time.sleep(2)
    app.set_model(cst.LLAMA370B)
    app.bouton_commencer_diction.invoke()
    # NB: Après cette invocation l'application est lancée en mode audioChat directement

    app.mainloop(0)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create a ArcHydro schema")
    parser.add_argument(
        "--prompt", metavar="prompt", required=False, help="the prompt to ask"
    )

    args: Namespace = parser.parse_args()

    main(prompt=args.prompt)
