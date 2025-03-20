"""
This script is the entry point for the ZicChatbotAudio application. It can run in two modes:
1. Terminal mode: If the --prompt argument is provided, the application will run in the terminal,
    process the prompt, and print the responses in the terminal before exiting.
2. GUI mode: If the --prompt argument is not provided, the application will launch a GUI window
    using Tkinter.
Functions:
     main(prompt=False, min: str = "3", max: str = "3", talk=False):
          Entry point of the app. Depending on the prompt argument, it either runs in terminal mode
          or launches the GUI.
Usage:
     Run the script with optional arguments to specify the mode and parameters:
     -p : the prompt to ask (if provided, runs in terminal mode)
     -m : the minimum number of steps (default is "3")
     -x : the maximum number of steps (default is "3")
     -t : the talker (optional)
Example:
     python zic_win_chat.py -p "Hello" -m "2" -x "5" -t "talker_name"
"""
from argparse import Namespace
import tkinter as tk

from FenetrePrincipale import FenetrePrincipale
import Constants as cst
from StoppableThread import StoppableThread
from outils import create_asyncio_task, lire, term_response

def main(prompt=False, min: str = "3", max: str = "3", talk=False):
    """
    Main function to run the ZicChatbotAudio application.
    Args:
        prompt (bool): If True, runs the terminal mode with the given prompt.
        min (str): Minimum value for the term_response function. Default is "3".
        max (str): Maximum value for the term_response function. Default is "3".
        talk (bool): If True, enables talk mode in the term_response function.
    If `prompt` is True, it starts a terminal mode thread and waits for it to complete.
    Otherwise, it initializes and runs the graphical user interface for the chatbot.
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
        lire("Bienvenue dans ZicChatbotAudio\n")
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
        "-p", metavar="prompt", required=False, help="the prompt to ask"
    )
    parser.add_argument(
        "-m", metavar="min", required=False, help="the min of steps"
    )
    parser.add_argument(
        "-x", metavar="max", required=False, help="the max of steps"
    )
    parser.add_argument("-t", metavar="talk", required=False, help="the talker")
    args: Namespace = parser.parse_args()

    # Début du programme
    main(
        prompt=args.p,
        min=args.m,
        max=args.x,
        talk=args.t,
    )
