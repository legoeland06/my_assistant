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

    parser = argparse.ArgumentParser(description="Parser d'options")
    parser.add_argument("-p", metavar="p", required=False, help="the prompt to ask")
    parser.add_argument(
        "-a", metavar="ahghg", required=False, help="the min of steps before answering"
    )
    parser.add_argument(
        "-b", metavar="b", required=False, help="the max of steps before answering"
    )
    parser.add_argument("-t", metavar="t", required=False, help="ask to read responses")
    args: Namespace = parser.parse_args()

    # Début du programme
    main(
        prompt=args.p,
        min=args.a,
        max=args.b,
        talk=args.t,
    )
