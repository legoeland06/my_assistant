# zic_chat.py
from argparse import Namespace
import tkinter as tk

from FenetrePrincipale import FenetrePrincipale
import Constants as cst
from StoppableThread import StoppableThread
from outils import (
    create_asyncio_task,
    lire,
    term_response,
)


def main(prompt=False, min: str = "3", max: str = "3", talk=False):
    """
    ### Entry point of the app ###
    * **If --prompt is True**, the application work in terminal
    and responses will be returned and printed in the terminal
    and exit programme
    """
    if prompt:
        _thread = StoppableThread(
            None,
            lambda: create_asyncio_task(
                async_function=term_response(
                    str(prompt),
                    min=min,
                    max=max,
                    talk=talk,
                )
            ),
        )
        _thread.name = "mode_terminal"
        _thread.start()
        _thread.join()
        exit()

    else:

        model_used = cst.LLAMA370B.split(":")[0]
        lire("Ia sélectionnée :" + model_used)
        print(
            "ZicChatbotAudio\n"
            + cst.STARS * cst.WIDTH_TERM
            + "\nChargement... Veuillez patienter\n"
            + cst.STARS * cst.WIDTH_TERM
        )

        root = tk.Tk(className="YourAssistant")
        root.title = "AssIstant - "  # type: ignore

        fenetre_principale = FenetrePrincipale(
            master=root, title="AssIstant", model_to_use=model_used
        )

        fenetre_principale.title = "MyApp"
        fenetre_principale.mainloop()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create a ArcHydro schema")
    parser.add_argument(
        "--prompt", metavar="prompt", required=False, help="the prompt to ask"
    )
    parser.add_argument(
        "--min", metavar="min", required=False, help="the min to ask"
    )
    parser.add_argument(
        "--max", metavar="max", required=False, help="the max to ask"
    )
    parser.add_argument("--talk", metavar="talk", required=False, help="the talker")
    args: Namespace = parser.parse_args()

    # Début du programme
    main(
        prompt=args.prompt,
        min=args.min,
        max=args.max,
        talk=args.talk,
    )
