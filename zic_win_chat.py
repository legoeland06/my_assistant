# zic_chat.py
from argparse import Namespace
import time
import tkinter as tk

# from tkinter import simpledialog
from tkinter import messagebox
from groq import Groq
import openai
from FenetrePrincipale import FenetrePrincipale
import Constants as cst
from outils import lire_haute_voix
from secret import GROQ_API_KEY


def ask_to_ai(agent_appel, prompt, model_to_use):

    print("PROMPT:: \n" + prompt)
    mytime = time.perf_counter_ns()
    ai_response = ""
    if isinstance(agent_appel, Groq):

        this_message = [
            {"role": "system", "content": ""},
            {"role": "assistant", "content": ""},
            {"role": "user", "content": prompt},
        ]

        try:
            llm: openai.ChatCompletion = agent_appel.chat.completions.create(  # type: ignore
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
    timing: float = (time.perf_counter_ns() - mytime) / cst.TIMING_COEF

    # TODO
    print(ai_response)

    return ai_response, timing

def traitement_rapide(texte: str, model_to_use, talking) -> str:
    groq_client = Groq(api_key=GROQ_API_KEY)

    ai_response, _timing = ask_to_ai(
        agent_appel=groq_client, prompt=texte, model_to_use=model_to_use
    )
    readable_ai_response = ai_response
    lire_haute_voix(readable_ai_response) if talking else None
    return readable_ai_response

def bypass_it(app: FenetrePrincipale):
    """
    ## Mode de développement ##
     BYPASS les sélection IHM chronophages en mode dev
     après cette invocation l'application est lancée en mode audioChat directement
    """
    groq_client = Groq(api_key=GROQ_API_KEY)
    app.set_client(groq_client)
    app.set_model(cst.LLAMA370B)
    app.bouton_commencer_diction.invoke()

def main(prompt=False):
    """
    ## Entry point of the app ##
    * If --prompt option is True, the application work in terminal
    and responses will be returned and printed in the terminal
    and exit programme
    """
    model_used = cst.LLAMA370B
    if prompt:
        traitement_rapide(str(prompt), model_to_use=model_used, talking=False)
        exit(0)

    model_used = cst.LLAMA370B.split(":")[0]
    lire_haute_voix("Ia sélectionnée :" + model_used)
    print(
        "ZicChatbotAudio\n"
        + cst.STARS * cst.WIDTH_TERM
        + "\nChargement... Veuillez patienter\n"
        + cst.STARS * cst.WIDTH_TERM
    )

    root = tk.Tk(className="YourAssistant")

    app = FenetrePrincipale(
        master=root,
        model_to_use=model_used,
    )
    root.title = "RootTitle - "  # type: ignore
    root.geometry("770x900")

    app.title = "MyApp"

    # Mode de développement
    # BYPASS les sélection IHM chronophages en mode dev
    bypass_it(app)
    # après cette invocation l'application est lancée en mode audioChat directement

    app.mainloop()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create a ArcHydro schema")
    parser.add_argument(
        "--prompt", metavar="prompt", required=False, help="the prompt to ask"
    )
    args: Namespace = parser.parse_args()

    # Début du programme
    main(prompt=args.prompt)
