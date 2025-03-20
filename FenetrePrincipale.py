"""
FenetrePrincipale is a class that represents the main window of the application.
It inherits from tk.Frame and provides various functionalities for managing
the user interface, handling user inputs, and interacting with AI models.
"""

import os
from asyncio.log import logger
from datetime import datetime
from secret import GROQ_API_KEY, GEMINI_API_KEY
import random
import time
from tkinter import filedialog, messagebox, simpledialog
from typing import Any, Tuple
from colorama import Fore
from groq import Groq
import ollama
from openai import ChatCompletion  # type: ignore
from Article import Article
from Constants import (
    CATEGORY_SEPARATOR,
    ZEFONT,
    IMAGE_PATH,
    LLAMA370B,
    DARK2,
    DARK3,
    RULS_RSS,
    BANNIERE_HEIGHT,
    LIGHT0,
    ANNULE,
    LIGHT3,
    URL_ACTU_GLOBAL_RSS,
    C_NOTE,
    MAX_HISTORY,
    CLICK_LIST,
    LIST_COMMANDS,
    LIGHT2,
    DARK1,
    RESPONSE,
    TIMING_COEF,
    YOU_SELECT_VALUE,
    ResponseList,
)
import tkinter.font as tkfont
import tkinter as tk
from PIL import Image, ImageTk
import threading

from Conversation import Conversation
from FenetreScrollable import FenetreScrollable
from GrandeFenetre import GrandeFenetre
from RechercheArticles import RechercheArticles
from SimpleMarkdownText import SimpleMarkdownText
from StoppableThread import StoppableThread
from google import genai
from google.genai import types
import my_feedparser_rss

from outils import (
    _traitement_du_texte,
    about_this_book,
    attentif,
    get_stream,
    lire_text_from_object,
    question_oui_non,
    recup_infos_rss_feed,
    reformat_text,
    threads_outils,
    append_saved_texte,
    ask_to_ai,
    ask_to_resume,
    charge_image,
    downloadimage,
    get_news_api,
    create_asyncio_task,
    lancer_chrome,
    lancer_search_chrome,
    lecteur_init,
    from_rgb_to_tkcolors,
    get_groq_ia_list,
    get_pre_prompt,
    get_engine,
    letters_to_number,
    lire,
    load_pdf,
    load_txt,
    make_resume,
    question_oui_non_annule,
    question_ouverte,
    read_text_file,
    tester_appelation,
    traitement_du_texte,
    translate_it,
)


type History = list[Conversation]


class FenetrePrincipale(tk.Frame):
    """
    FenetrePrincipale is a class that represents the main window of the application.
    It inherits from tk.Frame and provides various functionalities for managing
    the user interface, handling user inputs, and interacting with AI models.

    Attributes:
        master (tk.Tk): The root window of the application.
        model_to_use (str): The AI model to use.
        debride (bool): A flag indicating whether the application is in debride mode.
        history (list): A list to store the history of interactions.
        calice (list): A list to store the calice data.
        ai_response (str): The response from the AI.
        nb_mots (int): The number of words required for a valid prompt.
        threads (list): A list of threads.
        valide (bool): A flag indicating whether the prompt validation is enabled.
        ok_to_Read (bool): A flag indicating whether the AI responses should be read aloud.
        responses (list): A list to store the responses.
        submission (str): The current submission content.
        fenetre_scrollable (FenetreScrollable): The scrollable window.
        bouton_informations (tk.Button): The button to display information.
        bouton_active_debride (tk.Button): The button to activate debride mode.
        bouton_liste_actu (tk.Button): The button to display the list of news.
        bouton_effacer_historique (tk.Button): The button to clear history.
        bouton_historique (tk.Button): The button to display history.
        bouton_lire1 (tk.Button): The button to read the prompt.
        bouton_traduire_sur_place (tk.Button): The button to translate the prompt.
        bouton_commencer_diction (tk.Button): The button to start diction.
        bouton_soumetre (tk.Button): The button to submit the prompt.
        bouton_save_to_mp3 (tk.Button): The button to save text to mp3.
        bouton_load_pdf (tk.Button): The button to load a PDF file.
        bouton_load_txt (tk.Button): The button to load a TXT file.
        button_keywords (tk.Button): The button to display keywords.
        grandeFenetre (GrandeFenetre): The large window for displaying information.
        button_quit_mode_vocal (tk.Button): The button to quit vocal mode.
    Methods:
        * **__init__** (self, title: str, model_to_use: str, master): Initializes the FenetrePrincipale class.
        ---------------------------------------------------------
        * **all the getters and setters** : for self working attributes
        ---------------------------------------------------------
        * **save_to_submission** (self) -> bool: Saves the prompt to submission.
        * **debride_switch** (self, status): Switches the debride mode.
        * **delete_all_threads** (self): Deletes all threads.
        * **soumettre** (self) -> str: Submits the prompt.
        * **lance_thread_ecoute** (self): Launches the listening thread.
        * **get_synonymsOf** (self, expression): Gets synonyms of the given expression.
        * **dialog_ia** (self): Handles the AI dialog.
        * **mode_commandes_vocales** (self): Handles the vocal commands mode.
        * **process_vocal_commands** (self, ck_ecoute, multi_line): Processes the vocal commands.
        * **lancer_application** (self, ck_ecoute): Launches an application.
        * **command_quit_session** (self): Quits the session.
        * **get_all_news** (self): Gets all the news.
        * **display_search_list_results** (self, calice: list): Displays the search list results.
        * **recup_informations** (self, max_article_a_recup: int = 10): Recovers the information.
        * **extract_infos** (self, subject, max_article_a_recup: int): Extracts the information.
        * **save_to_history** (self, fenetre_name: str, question: str, ai_response: str): Saves the conversation to history.
        * **check_before_read** (self, response_to_read: str): Checks before reading the response.
        * **delete_last_discussion** (self): Deletes the last discussion.
        * **delete_history** (self): Deletes the history.
        * **display_help** (self) -> str: Displays the help window.
        * **display_listbox_actus** (self, final_list, mode_audio: bool = False): Displays the listbox for news.
        * **get_audio_news** (self, final_list: list): Gets the audio news.
        * **lancement_infos** (self, evt): Launches the information retrieval.
        * **load_and_affiche_txt** (self): Loads and displays a text file.
        * **load_and_affiche_pdf** (self): Loads and displays a PDF file.
        * **creer_fenetre** (self, msg_to_write): Creates the main window.
        * **textwidget_to_mp3** (self): Converts the text widget content to mp3.
        * **traduit_maintenant** (self): Translates the text.
        * **demander_actu** (self, evt: tk.Event): Asks for the news.
        * **lire_commande** (self, evt: tk.Event): Reads the command.
        * **affiche_ia_list** (self, list_to_check: list): Displays the list of AI models.
        * **get_prompts_history** (self) -> list: Gets the prompts history.
        * **supprimer_conversation** (self, evt: tk.Event): Deletes a conversation.
        * **print_liste_des_conversations** (self): Prints the list of conversations.
    """

    def __init__(
        self,
        title: str,
        # model ia à utiliser
        model_to_use: str,
        master,
    ):
        """
        Initialize the main window of the application.
        Args:
            title (str): The title of the window.
            model_to_use (str): The AI model to use.
            master: The parent widget.
        Attributes:
            master: The parent widget.
            pseudo (str): A placeholder username.
            debride (bool): A flag for some functionality (default is False).
            history (list): A list to store history.
            calice (list): Another list for storing data.
            searchHystory (list): A list to store search history.
            title (str): The title of the window.
            ai_response (str): A string to store AI responses.
            nb_mots (int): Number of words (default is 4).
            thread: A placeholder for a thread.
            threads (list): A list to store threads.
            valide (bool): A flag for validation (default is True).
            ok_to_Read (bool): A flag to check if it's okay to read (default is True).
            prompts_history (list): A list to store prompt history.
            responses (list): A list to store responses.
            submission (str): A string to store submissions.
            fontdict: Font settings for the application.
            default_font: Default font settings.
            btn_font: Button font settings.
            timer (float): A timer (default is 0).
            model_to_use (str): The AI model to use.
            image (ImageTk.PhotoImage): An image for the banner.
            image_button_diction1: An image for a button.
            image_button_diction2: Another image for a button.
            image_button_diction3: Another image for a button.
            image_link (str): A string to store image links.
            content (str): A string to store content.
            widgetMotcles (tk.Entry | None): An entry widget for keywords.
            my_liste (list): A list for storing data.
            messages (list): A list of messages with roles and content.
            actual_chat_completion (list): A list for storing chat completions.
            streaming: A stream object.
            fenetre_scrollable (FenetreScrollable): A scrollable window.
        """
        super().__init__(master)
        self.master = master
        self.pseudo = "kiki"
        self.debride = False
        self.history = []
        self.calice = []
        self.searchHystory = []
        self.title = title
        self.ai_response = str()
        self.nb_mots = 4
        self.thread = None
        self.threads = []
        self.valide = True
        self.ok_to_Read = True
        self.prompts_history = []
        self.responses = []
        self.submission = str()
        self.set_mode_prompt_off()
        self.fontdict = tkfont.Font(
            family=ZEFONT[0],
            size=ZEFONT[1],
            slant=ZEFONT[2],
            weight=ZEFONT[3],
        )
        self.default_font = tkfont.nametofont("TkDefaultFont")
        self.default_font.configure(size=14)
        self.btn_font = tkfont.nametofont("TkIconFont")
        self.btn_font.configure(size=14)
        self.timer: float = 0
        self.model_to_use = model_to_use
        self.image: ImageTk.PhotoImage = ImageTk.PhotoImage(
            Image.open(f"{IMAGE_PATH}/banniere.png").reduce(2)
        )  # type: ignore
        self.image_button_diction1 = charge_image(f"{IMAGE_PATH}/oeil1.jpg", 200)
        self.image_button_diction2 = charge_image(f"{IMAGE_PATH}/oeil2.jpg", 200)
        self.image_button_diction3 = charge_image(f"{IMAGE_PATH}/casque1.png", 200)

        self.image_link = str()
        self.content = str()
        self.widgetMotcles: tk.Entry | None = None

        # phase de construction de la fenetre principale
        self.creer_fenetre(
            msg_to_write="Prompt...",
        )
        self.my_liste = []
        self.messages = [
            {
                "role": "user",
                "content": "Bonjour",
            },
        ]
        self.actual_chat_completion = []
        self.streaming = get_stream()

        # Mode de développement
        # BYPASS les sélection IHM chronophages en mode dev
        self.bypass()
        # après cette invocation l'application est lancée en mode audioChat directement

        self.pack(fill="both", expand=False)
        self.fenetre_scrollable = FenetreScrollable(self.master)
        self.fenetre_scrollable.pack(fill="both", expand=True)

    #####################################################################################
    # DEBUT DES GETTERS SETTERS
    #####################################################################################

    def set_pseudo(self, pseudo: str):
        self.pseudo = pseudo

    def get_pseudo(self) -> str:
        return self.pseudo

    def bypass(self):
        """by pass les sélections dIa et de client"""

        clint = Groq(api_key=GROQ_API_KEY)
        self.set_client(client=clint)
        self.set_model(LLAMA370B)
        self.lance_thread_ecoute()

    def set_debride(self, status: bool):
        self.debride = status

    def get_debride(self) -> bool:
        return self.debride

    def set_ok_to_Read(self, ok_to_read: bool):
        """setter for chatAudioMode"""
        self.ok_to_Read = ok_to_read

    def get_ok_to_Read(self) -> bool:
        """getter for chatAudioMode"""
        return self.ok_to_Read

    def setValide(self, valide: bool):
        self.valide = valide

    def getValide(self) -> bool:
        return self.valide

    def getListOfModels(self):
        """
        Retrieves a list of model names from the Ollama API.

        Returns:
            list: A list of model names.
        """
        return [element["name"] for element in (ollama.list())["models"]]

    def get_actual_chat_completion(self) -> list:
        return self.actual_chat_completion

    def set_thread(self, thread: StoppableThread | None):
        """
        Sets the thread for the current instance.

        Args:
            thread (StoppableThread | None): The thread to be set. If None, the current thread will be removed from the list of threads.

        Raises:
            Exception: If there is no thread to remove, an exception will be caught and a message will be printed.
        """
        self.thread = thread
        if thread is None:
            try:
                threads_outils.remove(thread)
                lire("thread supprimée de la liste des threads")
            except Exception as e:
                print(f"aucune thread à supprimer : {e}")

    def get_thread(self) -> StoppableThread:
        return self.thread  # type: ignore

    def set_timer(self, timer: float):
        self.timer = timer

    def get_timer(self) -> float:
        return self.timer

    def set_ai_response(self, response: str):
        self.ai_response = response

    def get_ai_response(self) -> str:
        return self.ai_response

    # ici on pourra pointer sur un model hugginface plus rapide à répondre mais en ligne
    def set_client(self, client: Any):
        self.client = client
        # lire("changement du client : " + str(type(self.client)))

    def get_client(self) -> Any:
        return self.client

    def get_motcles(self) -> list[str]:
        """
        Retrieves a list of keywords from the widgetMotcles entry widget.

        This method checks if the widgetMotcles attribute is an instance of
        tk.Entry and if it contains any text. If both conditions are met, it
        splits the text into a list of keywords and returns it. Otherwise, it
        returns an empty list.

        Returns:
            list[str]: A list of keywords if widgetMotcles is a tk.Entry and
                   contains text, otherwise an empty list.
        """
        if (
            isinstance(self.widgetMotcles, tk.Entry)
            and self.widgetMotcles.get().__len__()
        ):
            motcles: list[str] = self.widgetMotcles.get().split()
            return motcles
        else:
            return []

    def get_mode_prompt(self):
        """
        Retrieve the current mode prompt.
        Returns:
            str: The current mode prompt.
        """

        return self.mode_prompt

    def set_mode_prompt_off(self):
        """
        ## ce booléen spécifie si les mots enregistrés du microphones
        * FALSE sont une commandes vocale elle doit etre effacée du prompt
        * TRUE sont un prompt et doivent être maintenues inchangées (initialisée comme telle par defaut)
        """
        self.mode_prompt = False
        return self.mode_prompt

    def set_mode_prompt_on(self):
        """
        ## ce booléen spécifie si les mots enregistrés du microphones
        * FALSE sont une commandes vocale elle doit etre effacée du prompt
        * TRUE sont un prompt et doivent être maintenues inchangées (initialisée comme telle par defaut)
        """
        self.mode_prompt = True
        return self.mode_prompt

    def set(self, content: str):
        self.content = content

    def get(self) -> str:
        return self.content

    def set_submission(self, content: str):
        """
        remplace tout le contenu de l'attribut **submission** de lma classe, par la valeur de **content**
        """
        self.submission = content

    def get_submission(self) -> str:
        return self.submission

    def get_image_link(self) -> str:
        return self.image_link

    def set_image_link(self, image_link: str):
        self.image_link = image_link

    def set_model(self, name_ia: str) -> bool:
        self.model_to_use = name_ia
        return True

    def get_model(self) -> str:
        return self.model_to_use

    def get_image(self) -> ImageTk.PhotoImage:
        return self.image

    def set_image(self, image: ImageTk.PhotoImage) -> bool:
        self.image = image
        return True

    #####################################################################################
    # FIN DES GETTERS SETTERS
    #####################################################################################

    # open a windows
    def affiche_banniere(self, image_banniere: ImageTk.PhotoImage, slogan):
        """
        Displays a banner with an image and a slogan on the main window.
        Args:
            image_banniere (ImageTk.PhotoImage): The image to be displayed on the banner.
            slogan (str): The slogan text to be displayed on the banner.
        This method creates a banner with the following components:
        - A main frame for the banner.
        - A sub-frame for buttons.
        - A canvas to display the banner image.
        - Several buttons with different functionalities:
            - Quit button
            - Groq choice button
            - Web status button
            - Enlarge text button
            - Decrease text button
            - Information button
            - Activate debride button
            - List news button
            - Deactivate debride button
        - A label to display the slogan text.
        """
        # ## PRESENTATION DU GOELAND  ####
        self.canvas_principal_banniere = tk.Frame(
            self, background=from_rgb_to_tkcolors(DARK2), name="cnvs1"
        )
        self.canvas_principal_banniere.pack(fill="x", expand=True)
        self.canvas_buttons_banniere = tk.Frame(
            self.canvas_principal_banniere, name="cnvs2"
        )
        self.canvas_buttons_banniere.configure(bg=from_rgb_to_tkcolors(DARK3))
        self.canvas_buttons_banniere.pack(fill="x", expand=False)

        # Create a canvas
        self.canvas_image_banniere = tk.Canvas(
            self.canvas_principal_banniere,
            height=BANNIERE_HEIGHT,
            background=from_rgb_to_tkcolors(DARK2),
            name="canva",
        )

        # Création d'un bouton pour quitter
        self.bouton_quitter = tk.Button(
            self.canvas_buttons_banniere,
            font=self.btn_font,
            relief="flat",
            text=" :: Quit :: ",
            border=0,
            command=self.ask_before_quit,
        )
        self.bouton_quitter.configure(background="black", foreground="red")
        self.bouton_quitter.pack(side=tk.LEFT)

        self.bouton_Groq = tk.Button(
            self.canvas_buttons_banniere,
            font=self.btn_font,
            text=" :: IA :: ",
            command=self.groq_choix_ia,
            relief="flat",
            highlightthickness=3,
            highlightcolor="yellow",
        )
        self.bouton_Groq.configure(foreground="red", background="black")
        self.bouton_Groq.pack(side=tk.LEFT)

        # self.bouton_LargePolice = tk.Button(
        #     self.canvas_buttons_banniere,
        #     font=self.btn_font,
        #     text="+",
        #     command=self.enlarge,
        #     relief="flat",
        #     highlightthickness=3,
        #     highlightcolor="yellow",
        # )
        # self.bouton_LargePolice.configure(foreground="red", background="black")
        # self.bouton_LargePolice.pack(side=tk.LEFT)

        # self.bouton_DiminuePolice = tk.Button(
        #     self.canvas_buttons_banniere,
        #     font=self.btn_font,
        #     text="-",
        #     command=self.diminue,
        #     relief="flat",
        #     highlightthickness=3,
        #     highlightcolor="yellow",
        # )
        # self.bouton_DiminuePolice.configure(foreground="red", background="black")

        self.bouton_informations = tk.Button(
            self.canvas_buttons_banniere,
            font=self.btn_font,
            text="  :: NEWS :: ",
            command=self.recup_inf,
            relief="flat",
            highlightthickness=3,
            highlightcolor="yellow",
            activeforeground="white",
        )
        self.bouton_informations.configure(foreground="red", background="black")

        self.bouton_informations.pack(side=tk.LEFT)

        self.bouton_active_debride = tk.Button(
            self.canvas_buttons_banniere,
            font=self.btn_font,
            text=" :: GOD_MODE ::",
            command=lambda: self.debride_switch(True),
            relief="flat",
            highlightthickness=3,
            highlightcolor="yellow",
            activeforeground="white",
        )
        self.bouton_active_debride.configure(foreground="darkgrey", background="black")

        self.bouton_liste_actu = tk.Button(
            self.canvas_buttons_banniere,
            font=self.btn_font,
            text=" :: LIST_ACTUS ::",
            command=lambda: create_asyncio_task(
                self.display_listbox_actus(
                    [
                        f"{item['title']} :: {item['content'].replace(CATEGORY_SEPARATOR,", ")}"
                        for item in RULS_RSS
                    ],
                    mode_audio=False,
                )
            ),
            relief="flat",
            highlightthickness=3,
            highlightcolor="yellow",
            activeforeground="white",
        )
        self.bouton_liste_actu.configure(foreground="red", background="black")

        self.bouton_desactive_debride = tk.Button(
            self.canvas_buttons_banniere,
            font=self.btn_font,
            text=" :: GOD_MODE ::",
            command=lambda: self.debride_switch(False),
            relief="flat",
            highlightthickness=3,
            highlightcolor="yellow",
            activeforeground="white",
        )
        self.bouton_desactive_debride.configure(foreground="yellow", background="black")

        self.bouton_liste_actu.pack(side=tk.LEFT)
        self.bouton_active_debride.pack(side=tk.LEFT)

        self.label_slogan = tk.Label(
            self.canvas_buttons_banniere,
            text=slogan+" :: "+datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            font=("Trebuchet Bold Italic", 8),
            bg="black",
            border=0,
            relief="flat",
            fg=from_rgb_to_tkcolors(LIGHT3),
        )

        self.label_slogan.pack(side=tk.RIGHT, expand=False)

        # Add the image to the canvas, anchored at the top-left (northwest) corner
        self.canvas_image_banniere.create_image(
            0, 0, anchor="nw", image=image_banniere, tags="bg_img"
        )
        self.canvas_image_banniere.pack(fill="x", expand=True)

    def save_to_submission(self) -> bool:
        """
        Saves the current selection or the entire content of the main prompt to the submission.
        If a selection is made in the main prompt, it is saved to the submission.
        Otherwise, the entire content of the main prompt is saved.
        Returns:
            bool: True if the content was successfully saved, False otherwise.
        """

        _ = self.entree_prompt_principal.get_text()
        if _.__len__():
            self.set_submission(_)
        else:
            return False
        return True

    def debride_switch(self, status):
        """
        Toggles the debride status and updates the UI accordingly.

        Parameters:
        status (bool): The new status to set for debride.

        This method sets the debride status using the set_debride method.
        It then checks the current debride status using the get_debride method.
        Depending on the debride status, it updates the UI by packing or
        forgetting the appropriate buttons.
        """
        self.set_debride(status=status)
        if self.get_debride():
            self.bouton_desactive_debride.pack(side=tk.LEFT)
            self.bouton_active_debride.pack_forget()
        else:
            self.bouton_active_debride.pack(side=tk.LEFT)
            self.bouton_desactive_debride.pack_forget()

    def ask_before_quit(self):
        """
        Display a confirmation message box asking the user if they are sure they want to quit.

        If the user confirms, the `quitter` method is called to quit the application.
        If the user cancels, a message is printed to the console.
        """
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir quitter ?"):
            self.quitter()
        else:
            print("L'utilisateur a annulé.")

    def quitter(self):
        """
        Closes the application gracefully.

        This method performs the following actions in order:
        1. Closes the current stream.
        2. Outputs a farewell message.
        3. Deletes all running threads.
        4. Waits for 2 seconds.
        5. Destroys the main window.
        6. Waits for 2 seconds.
        7. Quits the application.
        8. Waits for 2 seconds.
        9. Exits the program with status code 0.
        """
        get_stream().close()
        lire("au revoir !")
        self.delete_all_threads()
        time.sleep(2)
        self.master.destroy()
        time.sleep(2)
        self.quit()
        time.sleep(2)
        exit(0)

    def delete_all_threads(self):
        """
        Stops all running threads except the main thread.
        This method performs the following steps:
        1. Saves the current state to a submission.
        2. Iterates through all currently running threads and stops them if they are not the main thread.
        3. Iterates through the list of threads stored in `self.threads` and stops them if they are instances of `StoppableThread`.
        4. Iterates through the global `threads_outils` list and stops them if they are instances of `StoppableThread`.
        5. Prints the names of all threads that are currently running.
        Note:
            The `stop` method is assumed to be defined for instances of `StoppableThread`.
        """
        self.save_to_submission()
        mainthread = threading.main_thread()
        for i in threading.enumerate():
            if i != mainthread:
                print(f"ThreadThreading::{i.getName()}")
                i.stop()  # type: ignore

        for j in self.threads:
            if isinstance(j, StoppableThread):
                print(f"ThreadThreads::{j.getName()}")
                j.stop()

        for t in threads_outils:
            print(f"ThreadThreading::{t.getName()}")
            t.stop() if isinstance(t, StoppableThread) else None

        for element in threading.enumerate():
            print(f"threading_enumerated {element}")

    def enlarge(self):
        self.btn_font.configure(size=(self.btn_font.cget("size") + 2))
        self.fontdict.configure(size=(self.btn_font.cget("size") + 2))
        self.default_font.configure(size=(self.btn_font.cget("size") + 2))

    def diminue(self):
        self.btn_font.configure(size=(self.btn_font.cget("size") - 2))
        self.fontdict.configure(size=(self.btn_font.cget("size") - 2))
        self.default_font.configure(size=(self.btn_font.cget("size") - 2))

    def groq_choix_ia(self):
        """
        Initializes the Groq client and retrieves a list of available Groq AI models.

        This method performs the following steps:
        1. Creates an instance of the Groq client using the provided API key.
        2. Sets the created Groq client to the current instance.
        3. Retrieves a list of available Groq AI models using the provided API key.
        4. Displays the list of retrieved Groq AI models.

        Raises:
            Exception: If there is an error in initializing the Groq client or retrieving the models.

        Returns:
            None
        """
        groq_client = Groq(api_key=GROQ_API_KEY)
        self.set_client(groq_client)
        models = get_groq_ia_list(api_key=GROQ_API_KEY)
        self.affiche_ia_list(models)

    def soumettre(self) -> str:
        """
        Actions:
            Submits the current submission if it meets the required conditions.
            This method performs the following steps:
            1. Saves the current submission.
            2. Creates and starts a thread to handle the submission asynchronously.
            3. Checks the length of the submission.
            4. If the submission is too long (>= 3000 characters), it splits the
                submission into smaller blocks and processes each block in a separate thread.
            5. If the submission is within the acceptable length, it processes
                the submission in a single thread.
            6. Displays a message if no question is posed.
        Returns:
            str: A confirmation message indicating the submission status.
        """
        if self.save_to_submission():
            this_thread = StoppableThread(
                target=lambda: create_asyncio_task(async_function=self.asking())
            )
            this_thread.name = "submission"
            threads_outils.append(this_thread)
            lire("un instant s'il vous plait")
            _nb_chars = len(self.get_submission())
            print("nombre de charactères:: " + str(_nb_chars))
            if _nb_chars >= 3000:
                new_prompt_list = _traitement_du_texte(self.get_submission(), 200)
                lire(
                    "le prompt est trop long, il est supérieur à 3000 tokens, il sera découpé en "
                    + str(len(new_prompt_list))
                    + " blocs"
                )
                for number, bloc in enumerate(new_prompt_list):
                    print(str(number) + "\n" + " ".join(bloc))
                    self.set_submission(" ".join(bloc))
                    _this = StoppableThread(
                        target=lambda: create_asyncio_task(async_function=self.asking())
                    )
                    _this.name = "part_of_submission"
                    _this.start()
                    threads_outils.append(_this)

                    time.sleep(2)
            else:
                this_thread.start()

        else:
            messagebox.showinfo(
                message=self.get_synonymsOf("Veuillez poser au moins une question")
            )

        return "Ok c'est soummis"

    def lance_thread_ecoute(self):
        """
        Launches a new thread to listen for events if no existing thread named "mode_veille" is running.
        This method performs the following actions:
        1. Checks if a thread named "mode_veille" is already running. If so, it returns without doing anything.
        2. Updates the button image to indicate that the listening mode is active.
        3. Creates and starts a new thread named "mode_veille" that runs the `dialog_ia` asynchronous function.
        4. Sets the new thread as a daemon thread and starts it.
        5. Adds the new thread to the `threads_outils` list.
        6. Prints the details of the new thread for debugging purposes.
        Returns:
            None
        """
        if (
            self.get_thread() is not None
            and self.get_thread().getName() == "mode_veille"
        ):
            return None

        self.bouton_commencer_diction.configure(
            image=self.image_button_diction2,  # type: ignore
        )
        self.bouton_commencer_diction.update()

        self.set_thread(
            StoppableThread(
                None,
                name="mode_veille",
                target=lambda: create_asyncio_task(async_function=self.dialog_ia()),
            )
        )
        self.get_thread().daemon = True
        self.get_thread().start()
        threads_outils.append(self.get_thread())

        print("Infos Threads:\n***************************************")
        for element in self.get_thread().__dict__:
            print(element + "::" + str(self.get_thread().__dict__[element]))

        # self.get_thread().join()

    def get_synonymsOf(self, expression):
        prompt = f"en français exclusivement et sous la forme d'une liste sans puce, donne 20 façons différentes de dire : \
                ({expression}) "
        _ = genai.Client(api_key=GEMINI_API_KEY)
        if _:
            try:
                llm = _.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[prompt],
                    config={
                        # 'response_mime_type': 'application/json',
                        "response_schema": ResponseList,
                    },
                )

                ai_response = llm.parsed.model_dump()[ # type: ignore
                    "response"
                ]  # ["content"] # type: ignore
            except Exception as e:
                messagebox.Message(f"{e}")
                return expression
            ai_response_list = str(ai_response).splitlines()
            return ai_response_list[
                (
                    round(random.randint(1, (len(ai_response_list) - 1) * 10) / 10)
                    % (len(ai_response_list) - 1)
                )
                + 1
            ]
        return expression

    async def dialog_ia(self):
        _content: str = str()
        self.open_microphone()
        lire(
            "Bienvenue ! pour activer les commandes vocales, il suffit de dire : << passe en mode audio >>"
        )

        # entrez dans le mode veille
        if get_stream().is_stopped():
            get_stream().start_stream()

        _content = _content + await self.mode_veille()

        print("Sortie de mode interactif")

        return True

    async def mode_veille(self):
        content_commandes_vocales = str()
        self.set_mode_prompt_off()
        max_long = os.get_terminal_size().columns
        while True:
            if get_stream().is_stopped():
                get_stream().start_stream()

            check_ecoute: str = attentif()
            (
                print(
                    f"\n{Fore.CYAN}{'*' * max_long}\n{check_ecoute}\n{'*' * max_long}\n{Fore.RESET}"
                )
                if check_ecoute
                else None
            )

            if await self.handle_check_ecoute(check_ecoute, content_commandes_vocales):
                break

            if self.get_mode_prompt():
                content_commandes_vocales += " " + check_ecoute

        return content_commandes_vocales

    async def handle_check_ecoute(self, check_ecoute, content_commandes_vocales):
        if "afficher de l'aide" in check_ecoute:
            _ = self.display_help()
        elif "quel est le mode actuel" in check_ecoute:
            self.witch_mode("veille")
        elif any(keyword in check_ecoute for keyword in ["fermer", "ferme"]):
            if "l'application" in check_ecoute:
                await self.close_application(content_commandes_vocales)
                return True
        elif any(keyword in check_ecoute for keyword in ["active", "passe"]):
            await self.handle_active_commands(
                check_ecoute,
            )
        return False

    async def close_application(self, content_commandes_vocales):
        get_stream().stop_stream()
        self.bouton_commencer_diction.configure(image=self.image_button_diction1)  # type: ignore
        self.entree_prompt_principal.configure(bg=from_rgb_to_tkcolors(LIGHT0))
        self.bouton_commencer_diction.update()
        append_saved_texte(
            file_to_append="saved_text", readable_ai_response=content_commandes_vocales
        )
        lire(
            "ok, vous pouvez réactiver l'observeur audio en appuyant sur le bouton casque"
        )
        self.set_thread(None)

    async def handle_active_commands(self, check_ecoute):
        if any(
            keyword in check_ecoute for keyword in ["mode audio", "commandes vocales"]
        ):
            await self.activate_audio_mode()
        elif "mode débridé" in check_ecoute:
            self.debride_switch(True)
            lire("mode débridé activé")
        elif "mode normal" in check_ecoute:
            self.debride_switch(False)
            lire("mode debridé désactivé")

    async def activate_audio_mode(self):
        get_stream().stop_stream()
        self.bouton_commencer_diction.configure(image=self.image_button_diction3)  # type: ignore
        self.entree_prompt_principal.configure(
            bg=from_rgb_to_tkcolors((DARK3)), fg=from_rgb_to_tkcolors((182, 78, 20))
        )
        self.bouton_commencer_diction.update()
        lire("commande effectué, vous êtes en mode audio")
        get_stream().start_stream()
        self.open_microphone()
        await self.mode_commandes_vocales()

    async def mode_commandes_vocales(self):
        multi_line = str()
        self.setup_vocal_mode_ui()
        max_long = os.get_terminal_size().columns
        while not self.micro_is_cut:
            self.set_mode_prompt_on()
            ck_ecoute: str = attentif()
            (
                print(
                    f"\n{Fore.LIGHTRED_EX}{'*' * max_long}\n{ck_ecoute}\n{'*' * max_long}\n{Fore.RESET}"
                )
                if ck_ecoute
                else None
            )
            await self.process_vocal_commands(ck_ecoute, multi_line)
        return multi_line

    def setup_vocal_mode_ui(self):
        self.button_quit_mode_vocal = tk.Button(
            master=self.canvas_diction,
            text="MODE VEILLE",
            command=self.cut_microphone,
            background=from_rgb_to_tkcolors(DARK3),
            foreground=from_rgb_to_tkcolors(LIGHT3),
        )
        self.button_quit_mode_vocal.pack(side=tk.BOTTOM, fill="x", expand=True)

    async def process_vocal_commands(self, ck_ecoute, multi_line):
        command_handlers = {
            "afficher de l'aide": self.handle_help_command,
            "quel est le mode actuel": lambda: self.witch_mode("commandes vocales"),
            "quel jour sommes-nous": self.handle_date_command,
            "quelle heure est-il": self.handle_time_command,
            "est-ce que tu m'écoutes": self.handle_listening_command,
            "lancer une application": lambda: self.lancer_application(ck_ecoute),
            "effacer conversation": lambda: self.effacer_discussion(ck_ecoute),
            "affiche conversation": lambda: self.afficher_conversations(ck_ecoute),
            "affiche les actualités": lambda: self.affiche_actualites(ck_ecoute),
            "affiche toutes les actualités": self.get_all_news,
            "propos d'un livre": self.handle_book_command,
            "donne-moi les infos": self.get_informations,
            "faire une recherche web sur": lambda: self.recherche_web(ck_ecoute),
            "fin de la session": lambda: self.handle_end_session_command(
                multi_line, ck_ecoute
            ),
            "lis-moi systématiquement tes réponses": lambda: self.set_ok_to_Read(True),
            "arrêtez la lecture systématique des réponses": lambda: self.set_ok_to_Read(
                False
            ),
            "gérer les préférences": self.gerer_prefs,
            "la validation orale": lambda: self.handle_validation_command(ck_ecoute),
        }

        for command, handler in command_handlers.items():
            if command in ck_ecoute:
                if any(
                    keyword in command
                    for keyword in [
                        "donne-moi les infos",
                        "faire une recherche web sur",
                        "propos d'un livre",
                        "affiche les actualités",
                        "affiche toutes les actualités",
                    ]
                ):
                    await handler()
                else:
                    handler()

        if self.get_mode_prompt() and len(ck_ecoute.split()) >= self.nb_mots:
            multi_line = await self.valider_prompt(multi_line, ck_ecoute)

        try:
            get_stream().start_stream()
        except NameError as nerr:
            print(nerr)

    def handle_help_command(self):
        self.set_mode_prompt_off()
        _ = self.display_help()
        lire("état des lieux de la configuration du tchat intéractif")
        lire(
            "je vous lis systématiquement les réponses"
            if self.get_ok_to_Read()
            else "les réponses ne sont pas lues"
        )
        lire(
            "à la fin de votre question ou prompt valide, je vous demande si vous avez terminé"
            if self.getValide()
            else "dès lors que votre prompte est valide, je déclenche ma réponse."
        )
        lire(
            f"un prompt est valide dès lors qu'il contient au moins {str(self.nb_mots)} mots"
        )

    def handle_date_command(self):
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        lire("Nous sommes le " + time.strftime("%Y-%m-%d"))

    def handle_time_command(self):
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        lire("il est exactement " + time.strftime("%H:%M:%S", time.localtime()))

    def handle_listening_command(self):
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        lire(
            self.get_synonymsOf(f"oui je suis toujours à l'écoute {self.get_pseudo()}")
        )

    async def handle_book_command(self):
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        lire("choisissez votre texte d'investigation")
        book = load_txt(None)
        question = question_ouverte("quelle est votre question ?")
        print(f"Question:{question}")
        _response, _timer = await about_this_book(book, question)
        lire(_response)

    def handle_end_session_command(self, multi_line, ck_ecoute):
        get_stream().stop_stream()
        self.cut_microphone()
        return multi_line + " " + ck_ecoute

    def handle_validation_command(self, ck_ecoute):
        if any(keyword in ck_ecoute for keyword in ["active", "activer", "activez"]):
            get_stream().stop_stream()
            self.set_mode_prompt_off()
            self.setValide(True)
            lire(C_NOTE)
        elif any(keyword in ck_ecoute for keyword in ["stopper", "arrêter", "arrêtez"]):
            get_stream().stop_stream()
            self.set_mode_prompt_off()
            self.setValide(False)
            lire(C_NOTE)

    async def valider_prompt(self, multi_line, ck_ecoute):
        """
        Validates the prompt based on user input and processes it accordingly.
        This asynchronous method handles the validation of a prompt, interacts with the user to confirm if they have finished,
        and processes the input based on the user's response. It also interacts with an AI engine to generate responses.
        Args:
            multi_line (str): The current multi-line input from the user.
            ck_ecoute (str): The current line of input from the user.
        Returns:
            str: The updated multi-line input after processing the user's response.
        Behavior:
            - Stops the current stream.
            - If the input is valid, asks the user if they have finished.
                - If the user cancels, resets the engine and informs the user.
                - If the user confirms, sends the prompt to the AI engine and processes the response.
                - If the user continues, appends the current line to the multi-line input and prompts the user to continue.
            - If the input is not valid, sends the current line to the AI engine and processes the response.
        """
        get_stream().stop_stream()

        if self.getValide():
            result = question_oui_non_annule(
                "avez vous terminé ?",
            )

            if ANNULE == result:
                get_engine().Reset()
                lire("ok, j'efface votre phrase précédente")

            elif result:
                _response = await self.send_prompt(
                    multi_line + "\n" + ck_ecoute,
                    necessite_ai=True,
                    needed_groq=True,
                )
                await self.check_before_read(_response)
                multi_line = str()

            elif not result:
                multi_line += "\n" + ck_ecoute

                lire("continuez")

            del result

        else:
            _response = await self.send_prompt(
                ck_ecoute, necessite_ai=True, needed_groq=True
            )

            await self.check_before_read(_response)
        return multi_line

    def gerer_prefs(self):
        """
        Manages user preferences for the application.
        This method performs the following actions:
        1. Asks the user for the minimum number of words required to trigger a response.
           If the user input is invalid, it defaults to 4 words.
        2. Sets the user's pseudo (username) based on their input.
        3. Asks the user if they want an oral validation of their prompts.
        4. Asks the user if they want an oral response to their prompts.
        5. Sets the validation and oral response preferences based on user input.
        6. Sets the prompt mode to off.
        7. Provides a summary of the user's preferences.
        Returns:
            None
        """
        nbmot: int | bool = letters_to_number(
            question_ouverte(
                "à partir de combien de mots dois je déclencher ma réponse ?",
            )
        )

        if not nbmot:
            self.nb_mots = 4
        elif isinstance(nbmot, int):
            self.nb_mots = nbmot

        self.set_pseudo(question_ouverte("Quel est votre pseudo ?"))
        lire("merci")

        _question_validation = question_oui_non(
            "souhaitez vous une validation orale de vos prompt ?",
        )
        _question_ok_to_read = question_oui_non(
            "souhaitez vous une réponse orale de vos prompt ?",
        )
        self.setValide(valide=True if _question_validation else False)
        self.set_ok_to_Read(ok_to_read=True if _question_ok_to_read else False)

        self.set_mode_prompt_off()
        lire(
            f"c'est noté  {self.pseudo}: je récupère les prompts à partir de {str(self.nb_mots)} mots \
                     {"et je demande validation" if _question_validation else str() } avant de vous {"lire" if _question_ok_to_read else "afficher"} ma réponse."
        )

    async def recherche_web(self, ck_ecoute):
        """
        Performs a web search based on the provided input.
        This asynchronous method stops the current stream, disables prompt mode,
        modifies the input string to indicate a web search, sends the modified
        input to a prompt handler, and checks the response before returning the
        modified input.
        Args:
            ck_ecoute (str): The input string containing the search query.
        Returns:
            str: The modified input string indicating a web search.
        """
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        ck_ecoute = ck_ecoute.replace(
            " faire une recherche web sur", "\nrechercher sur le web : "
        )

        _websearching = await self.send_prompt(
            ck_ecoute, necessite_ai=True, needed_groq=False
        )
        await self.check_before_read(_websearching)
        return ck_ecoute

    async def get_informations(self):
        """
        Asynchronously retrieves and processes information based on user input.
        This method performs the following steps:
        1. Stops the current stream.
        2. Sets the mode prompt off.
        3. Prompts the user to input the number of articles to retrieve.
        4. Retrieves the articles based on the user's input.
        5. Asks the user if they want to hear the retrieved information.
        6. If the user agrees and articles are retrieved, prepares the articles for reading.
        7. Reads the prepared articles.
        8. Inserts the article information (title, description, content) into the main prompt.
        Returns:
            None
        """
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        _motcle, articles = await self.recup_informations(
            letters_to_number(
                question_ouverte(
                    "combien d'articles souhaitez vous que je tente de récupèrer ?",
                )
            )
        )
        if (
            question_oui_non(
                "voulez-vous que je lise ce que j'ai trouvé sur la recherche ?",
            )
            and isinstance(articles, list)
            and articles.__len__()
        ):
            _prepared: list = [
                f"Titre:{item.title}\nDescription:{item.description}\nContent:{item.content}"
                for item in articles
            ]
            _my_prepared = ask_to_resume(prompt="\n".join(_prepared))
            if _my_prepared:
                lire(str(_my_prepared))

            for article in articles:
                self.entree_prompt_principal.insert_markdown("# " + article.title)
                self.entree_prompt_principal.insert_markdown(
                    "## " + article.description
                )
                self.entree_prompt_principal.insert_markdown(article.content)

    async def affiche_actualites(self, ck_ecoute):
        """
        Asynchronously displays news based on the provided categories.
        This method stops the current stream and checks the provided categories
        to determine which news to display. If "africaines" is in the provided
        categories, it fetches all African news. Otherwise, it formats and displays
        a list of news items.
        Args:
            ck_ecoute (list): A list of categories to check for news.
        Returns:
            None
        """
        get_stream().stop_stream()

        if "africaines" in ck_ecoute:
            self.get_all_africa_news()
        else:
            final_list = [
                f"{n}. {item['title']} :: {item['content'].replace(CATEGORY_SEPARATOR,", ")}"
                for n, item in enumerate(RULS_RSS)
            ]
            _c, _t = await self.display_listbox_actus(final_list, mode_audio=True)

            self.set_mode_prompt_off()

    def afficher_conversations(self, ck_ecoute):
        """
        Affiche les conversations en fonction du mot-clé fourni.
        Args:
            ck_ecoute (str): Le mot-clé pour déterminer quelle conversation afficher.
        Actions:
            - Si le mot-clé contient "la liste des" ou "historique", affiche la liste des conversations.
            - Si le mot-clé contient "la dernière", affiche la dernière conversation.
            - Si le mot-clé contient "une", affiche une conversation spécifique.
        """
        if any(keyword in ck_ecoute for keyword in ["la liste des", "historique"]):
            self.affiche_liste()

        elif "la dernière" in ck_ecoute:
            self.affiche_derniere(ck_ecoute)

        elif "une" in ck_ecoute:
            self.affiche_une(ck_ecoute)

    def affiche_liste(self):
        """
        Stops the current stream, sets the mode prompt off, reads a message,
        and displays the history.

        This method performs the following actions:
        1. Stops the current audio stream.
        2. Disables the mode prompt.
        3. Reads the message "Voici".
        4. Displays the history.

        Returns:
            None
        """
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        lire("Voici")
        self.display_history()

    def affiche_derniere(self, ck_ecoute):
        """
        Handles the display and actions for the last conversation based on the given command.
        This method stops the current stream, sets the prompt mode off, and retrieves the last conversation.
        Depending on the command provided in `ck_ecoute`, it performs different actions:
        - If "affiche" is in `ck_ecoute`, it displays the conversation in an enlarged window.
        - If "archive" is in `ck_ecoute`, it creates a PDF of the conversation.
        - If "lis-moi" or "lis moi" is in `ck_ecoute`, it reads out the content of the last conversation.
        Args:
            ck_ecoute (str): The command indicating the action to be performed on the last conversation.
        """
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        _discussion: Conversation
        _conversation = self.responses[len(self.responses) - 1]
        _last_discussion: Conversation = self.nametowidget(_conversation)

        if "affiche" in ck_ecoute:
            _last_discussion.affiche_fenetre_agrandie()
        if "archive" in ck_ecoute:
            _last_discussion.create_pdf()
        elif any(keyword in ck_ecoute for keyword in ["lis-moi", "lis moi"]):
            lire(
                f"Contenu de la dernière conversation sur un total de {self.responses.__len__()} conversations enregistrées. "
                + _last_discussion.get_ai_response()
            )

    def affiche_une(self, ck_ecoute):
        """
        Handles the display, archiving, or reading of a specific conversation based on user input.
        Parameters:
        ck_ecoute (str): A string containing the command to execute. It can be one of the following:
                         - "affiche": To display the conversation in an enlarged window.
                         - "archive": To create a PDF of the conversation.
                         - "lis-moi", "lis moi", "dis-moi", "dis moi": To read the conversation aloud.
        The method prompts the user to specify which conversation to act upon, converts the input to a number,
        and performs the corresponding action if the conversation exists. If the specified conversation number
        exceeds the number of available conversations, it informs the user and exits the prompt mode.
        """
        zenumber: int = letters_to_number(
            question_ouverte(
                "laquelle ?",
            )
        )
        nb_conversations = len(self.responses)
        if zenumber <= nb_conversations:
            _conversation = self.responses[zenumber - 1]
            _discussion: Conversation = self.nametowidget(_conversation)
            _last_discussion: Conversation = self.nametowidget(_conversation)
            if "affiche" in ck_ecoute:
                _discussion.affiche_fenetre_agrandie()
            elif "archive" in ck_ecoute:
                _discussion.create_pdf()
            elif any(
                keyword in ck_ecoute
                for keyword in ["lis-moi", "lis moi", "dis-moi", "dis moi"]
            ):
                _last_discussion.lire()
            self.set_mode_prompt_off()

        else:
            self.set_mode_prompt_off()
            lire(
                "je suis désolé mais il n'y a pas plus de "
                + str(nb_conversations)
                + " conversations en mémoire"
            )

    def effacer_discussion(self, ck_ecoute):
        """
        Efface les discussions en fonction de l'option spécifiée dans ck_ecoute.
        Args:
            ck_ecoute (str): Une chaîne de caractères indiquant quelle discussion effacer.
                             Les valeurs possibles sont "historique", "la dernière", et "les dernières".
        Actions:
            - Si ck_ecoute contient "historique", arrête le flux, désactive le mode prompt et supprime tout l'historique.
            - Si ck_ecoute contient "la dernière", arrête le flux, désactive le mode prompt et supprime la dernière discussion.
            - Si ck_ecoute contient "les dernières", arrête le flux, désactive le mode prompt et demande combien de discussions
              doivent être supprimées, puis supprime ce nombre de dernières discussions.
        """
        if "historique" in ck_ecoute:
            get_stream().stop_stream()
            self.set_mode_prompt_off()
            self.delete_history()

        elif "la dernière" in ck_ecoute:
            get_stream().stop_stream()
            self.set_mode_prompt_off()
            self.delete_last_discussion()

        elif "les dernières" in ck_ecoute:
            get_stream().stop_stream()
            self.set_mode_prompt_off()
            for _ in range(letters_to_number(question_ouverte("combien ?"))):
                self.delete_last_discussion()

    def lancer_application(self, ck_ecoute):
        """
        Launches the application based on the provided keyword.

        This method stops the current stream, sets the prompt mode off, and then
        checks if any of the specified keywords ("internet", "chrome", "google")
        are present in the `ck_ecoute` parameter. If a keyword is found, it prompts
        the user for a search query and launches a Chrome search with the query.
        Otherwise, it prompts the user for an application name and launches Chrome
        with the specified application.

        Args:
            ck_ecoute (str): The keyword to determine the action to be taken.

        Returns:
            None
        """
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        if any(keyw in ck_ecoute for keyw in ["internet", "chrome", "google"]):
            lancer_search_chrome(
                question_ouverte(
                    "Que voulez vous chercher ?",
                ).replace(" ", "+")
            )
        else:
            lancer_chrome(
                tester_appelation(
                    question_ouverte(
                        "laquelle ?",
                    )
                )
                or str()
            )

    def witch_mode(self, mode: str):
        get_stream().stop_stream()
        self.set_mode_prompt_off()
        lire(f"nous sommes actuellement dans le mode {mode}")

    def cut_microphone(self):
        self.micro_is_cut = True
        self.button_quit_mode_vocal.destroy()
        self.command_quit_session()

    def open_microphone(self):
        self.micro_is_cut = False

    def command_quit_session(self):
        self.entree_prompt_principal.configure(
            bg=from_rgb_to_tkcolors(LIGHT0), fg=from_rgb_to_tkcolors(DARK3)
        )
        self.set_mode_prompt_off()

        self.bouton_commencer_diction.configure(
            image=self.image_button_diction2,  # type: ignore
        )
        self.bouton_commencer_diction.update()

        lire("merci. Pour ré-activer le mode commande vocales, il s'uffit de demander")
        time.sleep(1)

    def about_africa(self):
        rubrique = []
        feeds = [
            "https://www.africanews.com/feed/rss?themes=news,"
            "https://feeds.feedburner.com/AfricaIntelligence",
            "https://feeds.feedburner.com/LaLettre-fr",
            "https://feeds.feedburner.com/IntelligenceOnline/",
        ]
        max_long = os.get_terminal_size().columns
        for item in feeds:
            resultat = str()
            feed = my_feedparser_rss.feedparser.parse(item)

            for entry in feed.entries:
                resultat += translate_it(str(entry.title)) + "\n"
                resultat += translate_it(str(entry.description)) + "\n"

            print("\n" + "*" * max_long + "\n" + resultat + "\n" + "*" * max_long)
            rubrique.append(resultat)

        return rubrique

    def get_all_africa_news(self):
        self.calice = []
        lire("récupérations des actualités africaines en cours...")
        self.set_mode_prompt_off()
        recup = self.about_africa()
        print(f"longueur du resultat : {recup.__len__()}")
        print(recup[0])

    async def get_all_news(self):
        self.calice = []
        for liste_rss in URL_ACTU_GLOBAL_RSS:
            lire(
                "\nSujet: "
                + liste_rss["title"]
                + "\nRubriques: "
                + liste_rss["content"].replace(CATEGORY_SEPARATOR, ", ")
            )

            lire("récupérations des actualités globales en cours...")

            if "le monde informatique" in liste_rss["title"].lower():
                feed_rss = my_feedparser_rss.le_monde_informatique(
                    liste_rss["content"].split(" | ")
                )
            elif "global_search" in liste_rss["title"].lower():
                feed_rss = my_feedparser_rss.generic_search_rss(
                    rss_url=liste_rss["content"].split(" | "),
                    nombre_items=10,
                )
            else:
                feed_rss = my_feedparser_rss.lemonde(liste_rss["content"].split(" | "))

            self.set_mode_prompt_off()
            for category in map(translate_it, feed_rss):
                if category.__len__():
                    _response = await self.send_prompt(
                        content_discussion=make_resume(category),
                        necessite_ai=True,
                        needed_groq=False,
                    )
                    self.calice.append(_response)
                    # lire(_response)
                    time.sleep(4)
        self.display_search_list_results(self.calice)

    def display_search_list_results(self, calice: list):
        """
        Displays the search list results and allows the user to interact with the list.
        Args:
            calice (list): A list of news items to be displayed.
        Returns:
            None
        Behavior:
            - If the list is empty, the function returns immediately.
            - Asks the user if they want to see the archived news.
            - If the user agrees, displays the list of news items in a Listbox.
            - Allows the user to select an item from the Listbox to read.
            - Provides an option for the user to read all news items.
            - If the user declines to see the news, a message is displayed indicating silence.
        """
        if calice == []:
            return
        if question_oui_non(
            f"nous avons archivé {calice.__len__()} news, voulez-vous que je vous les présente"
        ):

            def lire_calice_news(evt: tk.Event):
                w: tk.Listbox = evt.widget
                idx = w.curselection()
                print(f"idx={str(idx)}")
                value: str = w.get(idx[0])

                print('You selected item : "%s"' % value)

                lire(str(calice[idx[0]]))

            _list = [f"{n}:: {element}" for n, element in enumerate(calice)]
            _list_good = [
                f"{n}:: {str(" ").join(element.split(":: ")[1].split()[:5])}"
                for n, element in enumerate(_list)
            ]
            _listbox = self.traite_listbox(_list_good, "actu_news")
            _listbox.bind(CLICK_LIST, func=lire_calice_news)
            _list_good.append(ANNULE)
            ze_choix = letters_to_number(
                question_ouverte("faites votre choix : ", _list_good)
            )
            if ze_choix:
                lire(str(calice[ze_choix]))
            else:
                if question_oui_non("Voulez vous que je lise tout ? "):
                    lire("d'accord, je vous lis tout rubrique par rubrique")
                    for element in calice:
                        lire(element)

                else:
                    lire(f"d'accord {self.pseudo}")
        else:
            lire(f"ok, je garde le silence {self.pseudo}")

    async def recup_infos(self):
        await self.recup_informations(20)

    async def recup_informations(self, max_article_a_recup: int = 10):
        """
        Asynchronously retrieves information based on specified keywords and inserts articles into the main window.
        Args:
            max_article_a_recup (int, optional): The maximum number of articles to retrieve. Defaults to 10.
        Returns:
            list or tuple: If keywords are provided, returns a list of articles. If no keywords are provided, returns a tuple containing the keyword and a list of articles.
        Raises:
            ValueError: If the keyword format is incorrect.
        Notes:
            - If keywords are provided, the function will split each keyword and its associated number of articles to retrieve.
            - If no keywords are provided, the function will prompt the user for a keyword and retrieve articles based on that keyword.
            - The retrieved articles are inserted into the main window using a separate thread.
        """

        def insert_article_to_grande_fenetre(motcle: str):
            """
            Inserts an article into the main window based on the given keyword.

            Args:
                motcle (str): The keyword to search for articles.

            Raises:
                TypeError: If `recherche_articles` is not an instance of `RechercheArticles`.

            Side Effects:
                - Appends `recherche_articles` to `self.searchHystory`.
                - Creates and starts a new thread to insert content into the main window.
            """
            if isinstance(recherche_articles, RechercheArticles):
                self.searchHystory.append(recherche_articles)
                t = StoppableThread(
                    target=recherche_articles.insert_content_in_grande_fenetre(
                        motcles=motcle, grande_fenetre=self.grandeFenetre
                    ),
                )
                t.name = "find_articles"
                threads_outils.append(t)
                t.start()

        self.grandeFenetre = GrandeFenetre(tk.Toplevel(None))
        if len(self.get_motcles()):
            for element in self.get_motcles():
                mot, nb = element.split(":")
                recherche_articles: RechercheArticles = self.extract_infos(
                    mot, int(nb) or max_article_a_recup
                )
                insert_article_to_grande_fenetre(motcle=mot)

            self.reconfigure_aera()
            return recherche_articles.articles
        else:
            motcle = question_ouverte(
                "sur quel sujet voulez-vous que j'oriente mes recherches ?",
            )
            if motcle == "les sujets d'actualité":
                lire("Très bien, je récupère les actus en général")
                motcle = str()
            else:
                lire("Très bien, je récupère tout sur " + motcle)

            # récupération des titres du jour
            recherche_articles = self.extract_infos(motcle, max_article_a_recup)

            lire(f"j'ai trouvé {recherche_articles.articles.__len__()} articles")

            insert_article_to_grande_fenetre(motcle=motcle)

            self.reconfigure_aera()

            return motcle, recherche_articles.articles

    def reconfigure_aera(self):
        self.grandeFenetre.area_info.configure(
            height=min(
                reformat_text(self.grandeFenetre.area_info.get_text(), 30).__len__(), 60
            )
        )
        self.grandeFenetre.update()

    def extract_infos(self, subject, max_article_a_recup: int):
        """
        Extracts information from news articles based on the given subject and maximum number of articles to retrieve.
        Args:
            subject (str): The subject or topic to search for in the news articles.
            max_article_a_recup (int): The maximum number of articles to retrieve.
        Returns:
            RechercheArticles: An object containing the status, total results, and a list of articles that match the search criteria.
        Raises:
            ValueError: If the response status is not 'ok' or if there is an issue with the API response.
        Notes:
            - The function filters out articles with titles containing the word "removed".
            - The function downloads the image associated with each article and resizes it to a width of 600 pixels.
        """
        _responses = get_news_api(subject)
        recherche_articles = RechercheArticles(
            status=_responses.json()["status"],
            articles=[],
            total_results=_responses.json()["totalResults"],
        )

        for n, article in enumerate(_responses.json()["articles"]):
            if n >= max_article_a_recup:
                break
            if "removed" not in str(article["title"]).lower():
                _transfert = Article(
                    source=article["source"],
                    author=article["author"],
                    title=article["title"],
                    description=article["description"],
                    url=article["url"],
                    url_to_image=article["urlToImage"],
                    published_at=article["publishedAt"],
                    content=article["content"],
                    image=downloadimage(article["urlToImage"], 600),
                )
                recherche_articles.articles.append(_transfert)
                print(str(n) + "/" + str(max_article_a_recup) + " ; ")

        return recherche_articles

    async def save_to_history(self, fenetre_name: str, question: str, ai_response: str):
        """
        Saves the current conversation to the history and manages the history size.
        This method saves the current conversation (question and AI response) to the history.
        If the history exceeds a predefined maximum number of conversations (MAX_HISTORY),
        it summarizes the oldest conversations, clears them from the history, and saves the summary.
        Args:
            fenetre_name (str): The name of the window where the conversation took place.
            question (str): The user's question.
            ai_response (str): The AI's response to the user's question.
        Returns:
            None
        """
        prompt = question[:499] if len(question) >= 500 else question
        _response = ai_response[:499] if len(ai_response) >= 500 else ai_response
        longueur = len(self.get_prompts_history())

        # A partir de 15 conversations,
        ## on fait un résumé des 10 anciennes conversations (MAX_HISTORY=15)
        if longueur >= MAX_HISTORY:
            conversation_resumee = await ask_to_resume(
                agent_appel=Groq(api_key=GROQ_API_KEY),
                prompt="".join(map(str, self.get_prompts_history())),
                model_to_use=LLAMA370B,
            )

            # on les efface
            self.get_prompts_history().clear()

            # on insère le résumé des conversations
            self.get_prompts_history().append(
                {
                    "fenetre_name": fenetre_name,
                    "prompt": "Résumé des conversations précédente",
                    "response": conversation_resumee,
                },
            )
            lire("un résumé des anciennes conversations à été effectué")
            if question_ouverte(
                "voulez-vous que je vous lise ce résumé ?",
            ):
                lire("Résumé des conversations précédente\n" + conversation_resumee)

        # Ajout de cette conversation dans la listes générale des conversations
        self.get_prompts_history().append(
            {
                "fenetre_name": fenetre_name,
                "prompt": ask_to_resume(self.get_client(), prompt, self.get_model()),
                "response": ask_to_resume(
                    self.get_client(), ai_response, self.get_model()
                ),
            },
        )

    async def check_before_read(self, response_to_read: str):
        """
        demande une confirmation avant de lire le résultat de la requette à haute voix
        """
        if self.get_ok_to_Read():
            lire(response_to_read)
        else:
            lire("voici !")

    # bubble aitable make workflow

    def recup_inf(self):
        """
        Starts a new thread to asynchronously retrieve information.
        This method creates a new `StoppableThread` that runs an asynchronous task
        to retrieve information by calling `self.recup_informations(20)`. The thread
        is named "recup_infos" and is added to the global `threads_outils` list.
        Note:
            The `StoppableThread` and `create_asyncio_task` functions, as well as
            the `threads_outils` list, must be defined elsewhere in the codebase.
        """

        this_thread = StoppableThread(
            target=lambda: create_asyncio_task(
                async_function=self.recup_informations(20)
            )
        )
        this_thread.name = "recup_infos"
        this_thread.start()
        threads_outils.append(this_thread)

    def delete_last_discussion(self):
        """
        efface la dérnière discussion
        """
        widget: tk.Widget = self.nametowidget(self.responses.pop())
        widget.destroy()

    def delete_history(self):
        """
        supprime l'historique des conversations,
        """
        while self.responses.__len__() > 0:
            self.delete_last_discussion()

        lire("historique effacé !")

    def display_help(self) -> str:
        """
        affiche une fenetre d'aide
        """
        frame = tk.Toplevel(name="fenetre_aide")
        self.help_infos = SimpleMarkdownText(
            master=frame,
            width=len(max(LIST_COMMANDS, key=len)),
        )
        scrollbar_infos = tk.Scrollbar(frame)
        scrollbar_infos.configure(command=self.help_infos.yview)

        self.help_infos.pack(side=tk.LEFT, fill="both")

        for item in LIST_COMMANDS:
            self.help_infos.insert_markdown(item)

        self.help_infos.configure(
            background=from_rgb_to_tkcolors((40, 0, 40)),
            foreground=from_rgb_to_tkcolors(LIGHT2),
            yscrollcommand=scrollbar_infos.set,
            padx=20,
            pady=10,
            wrap="word",
            state="disabled",
        )

        scrollbar_infos.pack(side=tk.RIGHT, fill="both")

        _sortie = self.help_infos.bind(CLICK_LIST, func=self.lire_commande)
        return _sortie

    async def display_listbox_actus(self, final_list, mode_audio: bool = False):
        """
        Asynchronously displays a list of news items in a Tkinter Listbox widget.
        Args:
            final_list (list): A list of news items to display.
            mode_audio (bool, optional): If True, fetches and plays audio news. Defaults to False.
        Returns:
            tuple: A tuple containing the submission result and a text vocal command.
        Raises:
            Exception: If there is an issue displaying the list or fetching audio news.
        """
        try:
            frame = tk.Toplevel(name="list_actu")
            _list_box = tk.Listbox(
                master=frame,
                # on doit retirer le " | " autant de fois qu'il est présent
                # dans la ligne
                width=min(
                    100,
                    max(
                        map(
                            len,
                            [
                                str(element).replace(CATEGORY_SEPARATOR, ", ")
                                for element in final_list
                            ],
                        )
                    ),
                ),
                justify="left",
                height=min(final_list.__len__(), 15),
            )
            scrollbar_listbox = tk.Scrollbar(frame)
            scrollbar_listbox.configure(command=_list_box.yview)

            _list_box.pack(side=tk.LEFT, fill="both")

            for item in final_list:
                _list_box.insert(tk.END, item)

            _list_box.configure(
                background=from_rgb_to_tkcolors(LIGHT3),
                foreground=from_rgb_to_tkcolors(DARK3),
                yscrollcommand=scrollbar_listbox.set,
            )

            scrollbar_listbox.pack(side=tk.RIGHT, fill="both")

            if not mode_audio:
                _ = _list_box.bind(CLICK_LIST, func=self.lancement_infos)
            else:
                july = await self.get_audio_news(final_list)
                if not july:
                    frame.destroy()
                else:
                    lire("récupérations des actualités terminée")

        except Exception as e:
            print(f"{e}")
            lire("oups problème de liste d'information")

        finally:
            text_vocal_command = str()

        return self.get_submission(), text_vocal_command

    async def get_audio_news(self, final_list: list):
        """
        Asynchronously retrieves and processes audio news based on user-selected categories.
        Args:
            final_list (list): A list of categories to choose from.
        Returns:
            None
        Workflow:
            1. Appends a cancellation option to the final_list.
            2. Prompts the user to select a category and converts the response to a number.
            3. If a valid category is selected:
                a. Retrieves RSS feed information for the selected category.
                b. Translates the feed items.
                c. Announces the number of items to be processed.
                d. Clears the current list of processed items.
                e. Iterates through the translated feed items:
                    i. Sends each item to an AI service for summarization.
                    ii. Appends the summarized item to the list of processed items.
                    iii. Pauses briefly between requests.
                f. Displays the results of the search.
            4. If no valid category is selected, prompts the user to continue.
        Note:
            - Utilizes various helper functions such as `letters_to_number`, `question_ouverte`, `recup_infos_rss_feed`, `translate_it`, `make_resume`, and `lire`.
            - Uses asynchronous operations and may involve network requests.
        """
        final_list.append(ANNULE)
        response_rubrique = letters_to_number(
            question_ouverte(
                "Quelle rubrique voulez-vous que je recherche pour vous ?",
                choix=final_list,
            )
        )
        if response_rubrique:
            rubrique_info = RULS_RSS[int(response_rubrique)]
            lire(f"Parfait, je recherche des informations sur {rubrique_info["title"]}")
            feed_rss = recup_infos_rss_feed(
                content_selected=rubrique_info["content"],
                value=rubrique_info["title"],
            )

            translated_feeds = list(map(translate_it, feed_rss))
            for item in translated_feeds:
                print(f"Traduction auto --> {item}")

            lire(f"Il y aura {len(translated_feeds)} intitulés à récupérer")
            self.calice.clear()
            for i, subject in enumerate(translated_feeds):
                if str(subject).split().__len__() > 1:
                    kiki = await self.send_prompt(
                        content_discussion=make_resume(subject),
                        necessite_ai=True,
                        needed_groq=True,
                    )
                    self.set_submission(self.get_submission() + kiki)
                    self.calice.append(kiki)
                    # lire(f"Sujet {i}:   {str(subject)}")

                    time.sleep(4)
            self.display_search_list_results(self.calice)

        else:
            lire("Pardons, veuillez continuez")
            return False

    def lancement_infos(self, evt):
        """
        Handles the event to launch information retrieval in a separate thread.

        This method creates a new `StoppableThread` to run the `demander_actu`
        coroutine asynchronously. The thread is named "demande_actu" and started
        immediately. The thread is then appended to the `threads_outils` list.

        Args:
            evt: The event that triggers the information retrieval.
        """
        _thread = StoppableThread(
            target=lambda: create_asyncio_task(self.demander_actu(evt))
        )
        _thread.name = "demande_actu"
        _thread.start()
        threads_outils.append(_thread)

    def marge_text(self, texte):
        long_text = len(texte)
        if long_text > 10:
            marge = int(long_text - (long_text / 4))
            print(
                (
                    texte.lower()[: int((long_text / 4))]
                    + " . . . "
                    + texte.lower()[marge:]
                )
                if long_text > 10
                else texte.lower()
            )
        else:
            print(texte)

    async def send_prompt(
        self, content_discussion, necessite_ai: bool, needed_groq: bool
    ) -> str:
        """
        Sends a prompt to the AI and processes the response.
        Args:
            content_discussion (str): The content of the discussion to be sent.
            necessite_ai (bool): Flag indicating whether AI response is needed.
            needed_groq (bool): Flag indicating whether to use Groq AI.
        Returns:
            str: The AI response if `necessite_ai` is True, otherwise the original content_discussion.
        """
        self.set_submission(content=content_discussion)
        self.entree_prompt_principal.clear_text()
        self.entree_prompt_principal.insert_markdown(mkd_text=content_discussion)
        self.save_to_submission()

        # ask question to AI and get (response,timing)
        if necessite_ai:
            if needed_groq:
                response, timing = await self.demander_ai_groq()
            else:
                response, timing = await self.demander_ai()

        # check if exist else initialize it
        if not self.fenetre_scrollable.winfo_exists():
            self.fenetre_scrollable = FenetreScrollable(self)

        # ajoute la réponse à la fenetre scrollable
        self.addthing(
            _timing=timing if necessite_ai else 0,
            agent_appel=self.get_client(),
            simple_text=content_discussion,
            ai_response=response if necessite_ai else content_discussion,
            model=self.get_model(),
            submit_func=self.soumettre,
        )

        return response if necessite_ai else content_discussion

    async def demander_ai_groq(self) -> Tuple[str, float]:
        response, timing = await ask_to_ai(
            agent_appel=self.get_client(),
            prompt=self.get_submission(),
            model_to_use=self.get_model(),
            motcle=self.get_motcles(),
            p_history=self.get_prompts_history(),
        )
        return str(response), timing

    async def demander_ai(self) -> Tuple[str, float]:
        """vérifie aussi le texte pour faire des recherches web"""
        prompt = self.get_submission()
        if isinstance(prompt, list):
            prompt = "\n".join(
                prompt
            )  # Convertir en liste si c'est une chaîne de caractères

        response, timing = await ask_to_ai(
            self.get_client(),
            prompt,
            model_to_use=self.get_model(),
            motcle=self.get_motcles(),
            p_history=self.get_prompts_history(),
        )

        return str(response), timing

    def go_submit(self, _evt):
        self.soumettre()

    def prompt_history_to_textlines(self, history) -> list:
        sortie = []
        for element in history:
            sortie.append(
                str(
                    datetime.now().ctime()
                    + "\n"
                    + "NameOfPrompt:: "
                    + element["fenetre_name"]
                    + "\n"
                    + "Prompt:: "
                    + element["prompt"]
                    + "\n"
                    + RESPONSE
                    + element["response"]
                    + "\n"
                )
            )
        return sortie

    async def asking(self) -> str:
        """
        Asynchronously sends a prompt to an AI model and processes the response.
        If the instance is in "debride" mode, it modifies the submission text before sending it to the AI.
        Sends the prompt to the AI model using the `ask_to_ai` function and processes the response.
        Args:
            None
        Returns:
            str: The readable response from the AI model.
        """
        if self.get_debride():
            self.set_submission(" \n en mode débridé \n" + self.get_submission())

        response_ai, _timing = await ask_to_ai(
            agent_appel=self.get_client(),
            prompt=self.get_submission(),
            model_to_use=self.get_model(),
            motcle=self.get_motcles(),
            p_history=self.get_prompts_history(),
        )
        readable_ai_response = str(response_ai)
        self.set_ai_response(readable_ai_response)

        self.addthing(
            _timing=_timing,
            agent_appel=self.get_client(),
            simple_text=self.entree_prompt_principal.get_text(),
            ai_response=self.get_ai_response(),
            model=self.get_model(),
            submit_func=self.soumettre,
        )

        return readable_ai_response

    def load_txt(self):
        """
        Opens a file dialog to select a text file, reads its content, and inserts the content
        into the main prompt area in markdown format.
        This method performs the following steps:
        1. Opens a file dialog to allow the user to select a text file.
        2. Reads the content of the selected file.
        3. Converts the content into a format suitable for markdown insertion.
        4. Inserts the formatted content into the main prompt area.
        If an error occurs during any of these steps, an error message is displayed.
        Raises:
            Exception: If there is an issue with reading the file or inserting the content.
        """
        try:
            file_to_read = filedialog.askopenfile(
                parent=self,
                title="ouvrir un txt",
                defaultextension="txt",
                mode="r",
                initialdir=".",
            )
            print(file_to_read.name)  # type: ignore
            resultat_txt = read_text_file(file_to_read.name)  # type: ignore
            lire("Fin de l'extraction")
            # on prepare le text pour le présenter à la méthode insert_markdown
            # qui demande un texte fait de lignes séparées par des \n
            # transforme list[str] -> str
            self.entree_prompt_principal.insert_markdown(mkd_text="".join(resultat_txt))

        except Exception as e:
            print(f"{e}")
            messagebox("Problème avec ce fichier txt")  # type: ignore

    def load_and_affiche_txt(self):
        resultat_txt: str = load_txt(self)
        self.entree_prompt_principal.insert_markdown(mkd_text=resultat_txt)

    def load_and_affiche_pdf(self):
        resultat_txt: str = load_pdf(self)
        self.entree_prompt_principal.insert_markdown(mkd_text=resultat_txt)

    def paste_clipboard(self):
        self.entree_prompt_principal.clear_text()
        self.entree_prompt_principal.insert_markdown(self.clipboard_get())

    def clear_entree_prompt_principal(self):
        self.entree_prompt_principal.clear_text()

    def traite_listbox(self, list_to_check: list, name: str = "list_ia") -> tk.Listbox:
        """
        Creates a new Toplevel window containing a Listbox widget populated with the provided list.
        Args:
            list_to_check (list): The list of items to populate the Listbox with.
            name (str, optional): The name of the Toplevel window. Defaults to "list_ia".
        Returns:
            tk.Listbox: The Listbox widget containing the items from the provided list.
        """
        frame = tk.Toplevel(name=name)
        frame.grid_location(self.winfo_x() + 150, self.winfo_y() + 130)
        _list_box = tk.Listbox(
            master=frame,
            font=self.default_font,
            width=100,
            height=list_to_check.__len__(),
        )
        scrollbar_listbox = tk.Scrollbar(frame)
        scrollbar_listbox.configure(command=_list_box.yview)

        _list_box.pack(side=tk.LEFT, fill="both")
        for item in list_to_check:
            _list_box.insert(tk.END, item)
        _list_box.configure(
            background="red",
            foreground=from_rgb_to_tkcolors(DARK3),
            yscrollcommand=scrollbar_listbox.set,
        )
        scrollbar_listbox.pack(side=tk.RIGHT, fill="both")

        return _list_box

    def charge_preprompt(self, evt: tk.Event):
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
                prompt_name=" ".join(self.get_motcles()).lower(),
            )

            self.entree_prompt_principal.insert_markdown(
                "**en mode débridé**, \n" + preprompt
            )

            lire("en mode débridé, " + preprompt)

        except Exception as e:
            print(f"{e} : aucun préprompt sélectionné")
        finally:
            if w.focus_get() is not None:
                w.focus_get().destroy()  # type: ignore

    def stoppeur(self):
        lecteur = lecteur_init()
        if lecteur._inLoop:
            lecteur.endLoop()
            lecteur.stop()

    def affiche_prepromts(self, list_to_check: list):
        """
        Affiche une boîte de dialogue pour entrer un mot-clé, met à jour les mots-clés de la classe,
        et affiche une liste d'éléments à vérifier.
        Args:
            list_to_check (list): Liste des éléments à afficher dans la Listbox.
        Fonctionnement:
        1. Ouvre une boîte de dialogue pour entrer un mot-clé.
        2. Met à jour l'attribut 'motcles' de la classe avec le mot-clé entré.
        3. Met à jour le widget tk.Entry avec le mot-clé entré.
        4. Crée et affiche une Listbox remplie avec les éléments de 'list_to_check'.
        5. Lie l'événement de sélection d'un item de la Listbox à la fonction 'charge_preprompt'.
        """
        # ouvre une boite dialog et récupère la sortie
        mots_cle = (
            simpledialog.askstring(
                title="YourAssistant - pré-prompts",
                initialvalue="Python",
                prompt="Veuillez entrer le mot-clé à traiter",
            )
            or str()
        )

        # on set l'attribut motcle de la classe
        self.get_motcles().extend(mots_cle.split())

        # on récupère le tk.Entry de la fenetre principale : frame_of_buttons_principal.motcles_widget
        # on le clean et on y insère le thème récupéré par la simpledialog auparavant
        if isinstance(self.widgetMotcles, tk.Entry):
            self.widgetMotcles.select_from(0)
            self.widgetMotcles.select_to(tk.END)
            self.widgetMotcles.select_clear()
            self.widgetMotcles.insert(0, mots_cle)

        # crée et affiche une _listbox remplie avec la variable list_to_check
        _listbox: tk.Listbox = self.traite_listbox(list_to_check)

        # bind sur l'événement sélection d'un item de la liste
        # vers la fonction charge_preprompt
        _listbox.bind(CLICK_LIST, func=self.charge_preprompt)

    def creer_fenetre(self, msg_to_write):  # type: ignore
        """
        Méthode de création de la fenêtre principale.
        Cette méthode configure et affiche la fenêtre principale de l'application avec divers widgets et boutons.
        Args:
            msg_to_write (str): Le message à écrire dans le widget de texte principal.
        Widgets créés:
            - Canvas pour l'espace de saisie des prompts.
            - Frame pour les boutons principaux.
            - Frame pour le prompt actuel.
            - SimpleMarkdownText pour l'entrée du prompt principal.
            - Boutons pour coller depuis le presse-papiers, effacer l'historique, afficher l'historique, lire le texte, traduire, dicter, soumettre, sauvegarder en MP3, charger un PDF, et charger un fichier TXT.
            - Entry pour les mots-clés.
        """

        # préparation de l'espace de saisie des prompts

        self.affiche_banniere(
            image_banniere=self.image,
            slogan="... Jonathan LivingStone, dit legoeland... ",
        )

        self.master_frame_actual_prompt = tk.Canvas(
            self,
            relief="sunken",
            name="master_frame_actual_prompt",
        )
        self.master_frame_actual_prompt.pack(side=tk.BOTTOM, fill="both", expand=False)
        self.frame_of_buttons_principal = tk.Frame(
            self.master_frame_actual_prompt,
            relief="sunken",
            name="frame_of_buttons_principal",
        )
        self.frame_of_buttons_principal.configure(
            background=from_rgb_to_tkcolors(DARK3)
        )
        self.frame_of_buttons_principal.pack(fill="x", expand=True)

        self.frame_actual_prompt = tk.Frame(
            self.master_frame_actual_prompt,
            relief="sunken",
            name="frame_actual_prompt",
            bg="black",
        )
        self.frame_actual_prompt.pack(fill="x", expand=True)

        self.entree_prompt_principal = SimpleMarkdownText(
            self.frame_actual_prompt,
            height=10,
            font=self.default_font,
            name="entree_prompt_principal",
        )

        self.entree_prompt_principal.widgetName = "entree_prompt_principal"

        # Attention la taille de la police, ici 10, ce parametre
        # tant à changer le cadre d'ouverture de la fenetre
        self.entree_prompt_principal.configure(
            bg=from_rgb_to_tkcolors(LIGHT0),
            fg=from_rgb_to_tkcolors(DARK3),
            font=self.default_font,
            wrap="word",
            padx=10,
            pady=6,
            undo=True,
        )

        self.boutton_paste_clipboard = tk.Button(
            self.frame_of_buttons_principal,
            font=self.btn_font,
            relief="flat",
            text="✔",
            fg="green",
            command=self.paste_clipboard,
        )
        self.boutton_effacer_historique = tk.Button(
            self.frame_of_buttons_principal,
            font=self.btn_font,
            relief="flat",
            text="🚫",
            fg="blue",
            bg=from_rgb_to_tkcolors(LIGHT3),
            command=self.delete_history,
        )
        self.boutton_historique = tk.Button(
            self.frame_of_buttons_principal,
            font=self.btn_font,
            relief="flat",
            text="📆",
            command=self.display_history,
        )
        self.boutton_historique.pack(side="right")
        self.boutton_paste_clipboard.pack(side="right")
        self.boutton_effacer_historique.pack(side="right")
        self.scrollbar_prompt_principal = tk.Scrollbar(self.frame_actual_prompt)
        self.scrollbar_prompt_principal.pack(side=tk.RIGHT, fill="both")

        self.entree_prompt_principal.insert_markdown(
            mkd_text=msg_to_write + " **< CTRL + RETURN > pour valider.**"
        )
        self.entree_prompt_principal.focus_set()
        self.entree_prompt_principal.pack(side="right", fill="x", expand=True)
        self.entree_prompt_principal.configure(
            yscrollcommand=self.scrollbar_prompt_principal.set
        )

        self.entree_prompt_principal.bind("<Control-Return>", func=self.go_submit)

        # Création d'un champ de saisie de l'utilisateur
        self.scrollbar_prompt_principal.configure(
            command=self.entree_prompt_principal.yview, bg=from_rgb_to_tkcolors(DARK2)
        )

        # Création d'un bouton pour Lire
        self.bouton_lire1 = tk.Button(
            self.frame_of_buttons_principal,
            activebackground=from_rgb_to_tkcolors((255, 0, 0)),
            activeforeground=from_rgb_to_tkcolors((0, 255, 255)),
            relief="flat",
            font=self.btn_font,
            text=chr(9654),
            command=lambda: lire_text_from_object(object=self.entree_prompt_principal),
        )
        self.bouton_lire1.configure(
            bg=from_rgb_to_tkcolors(DARK3),
            fg=from_rgb_to_tkcolors(LIGHT3),
            highlightbackground="red",
            highlightcolor=from_rgb_to_tkcolors(LIGHT3),
            activebackground="red",
        )
        self.bouton_lire1.pack(side=tk.LEFT)

        # Création d'un bouton pour traduction_sur_place
        self.bouton_traduire_sur_place = tk.Button(
            self.frame_of_buttons_principal,
            font=self.btn_font,
            relief="flat",
            text="Translate",
            command=self.traduit_maintenant,  # type: ignore
        )
        self.bouton_traduire_sur_place.configure(
            bg=from_rgb_to_tkcolors(DARK2),
            fg=from_rgb_to_tkcolors(LIGHT3),
            highlightbackground="red",
            highlightcolor=from_rgb_to_tkcolors(LIGHT3),
        )
        self.bouton_traduire_sur_place.pack(side=tk.LEFT)
        self.canvas_diction = tk.Canvas(self.frame_actual_prompt)

        # Création d'un bouton pour Dicter
        self.bouton_commencer_diction = tk.Button(
            self.canvas_diction,
            bg="black",
            image=self.image_button_diction1,  # type: ignore
            command=self.lance_thread_ecoute,
            relief="flat",
        )
        self.canvas_diction.pack(side=tk.LEFT, fill="x", expand=True)
        self.bouton_commencer_diction.pack(side=tk.TOP, fill="x", expand=True)

        # Création d'un bouton pour soumetre
        self.bouton_soumetre = tk.Button(
            self.frame_of_buttons_principal,
            relief="flat",
            font=self.btn_font,
            text="🅰ℹ",
            fg="blue",
            command=self.soumettre,
        )

        self.bouton_soumetre.configure(
            bg=from_rgb_to_tkcolors(LIGHT3),
            highlightbackground="blue",
            highlightcolor=from_rgb_to_tkcolors(LIGHT3),
        )
        self.bouton_soumetre.pack(side=tk.LEFT)

        self.bouton_save_to_mp3 = tk.Button(
            self.frame_of_buttons_principal,
            font=self.btn_font,
            relief="flat",
            text="txt \u261b mp3",
            command=self.textwidget_to_mp3,
        )
        self.bouton_save_to_mp3.configure(
            bg=from_rgb_to_tkcolors(DARK1), fg=from_rgb_to_tkcolors(LIGHT3)
        )
        self.bouton_save_to_mp3.pack(side="left")

        self.bouton_load_pdf = tk.Button(
            self.frame_of_buttons_principal,
            font=self.btn_font,
            text="📂 Pdf",
            relief="flat",
            command=self.load_and_affiche_pdf,
        )
        self.bouton_load_pdf.configure(
            bg=from_rgb_to_tkcolors(DARK2), fg=from_rgb_to_tkcolors(LIGHT3)
        )
        self.bouton_load_pdf.pack(side="left")

        self.bouton_load_txt = tk.Button(
            self.frame_of_buttons_principal,
            font=self.btn_font,
            relief="flat",
            text="📂 TXT",
            command=self.load_and_affiche_txt,
        )
        self.bouton_load_txt.configure(
            bg=from_rgb_to_tkcolors(DARK3), fg=from_rgb_to_tkcolors((255, 255, 255))
        )
        self.bouton_load_txt.pack(side="left")

        self.widgetMotcles = tk.Entry(
            self.frame_of_buttons_principal,
            name="motcles_widget",
            relief="flat",
            width=50,
            fg="red",
            bg=from_rgb_to_tkcolors(DARK3),
            font=("trebuchet", 10, "bold"),
        )
        self.button_keywords = tk.Button(
            self.frame_of_buttons_principal,
            font=self.btn_font,
            text="📌",
            relief="flat",
            background=from_rgb_to_tkcolors(DARK2),
            foreground=from_rgb_to_tkcolors(LIGHT3),
            command=lambda: self.affiche_prepromts(PROMPTS_SYSTEMIQUES.keys()),  # type: ignore
        )
        self.button_keywords.pack(side=tk.RIGHT, expand=False)
        self.widgetMotcles.pack(side="left", fill="x", padx=2, pady=2)

    def textwidget_to_mp3(self):
        """
        #### txt vers mp3
        Transforme le text sélectionné dans l'object de type
        SimpleMarkdownText donné en parametre en dictée mp3.
            Si rien n'est sélectionné, tout le text est traité.
        """
        obj: SimpleMarkdownText = self.entree_prompt_principal

        if None == obj.get_selected():
            # on récupère tout le contenu de l'objet
            texte_to_save_to_mp3 = obj.get("1.0", tk.END)
        else:
            texte_to_save_to_mp3 = obj.get_selected()

        if None != texte_to_save_to_mp3:
            if len(str(texte_to_save_to_mp3)) > 0:

                lire("transcription du texte vers un fichier mp3")
                file_name_mp3 = (
                    simpledialog.askstring(
                        parent=self,
                        prompt="Enregistrement : veuillez choisir un nom au fichier",
                        title="Enregistrer vers audio",
                    )
                    or "my_texte"
                )
                lecteur_init().save_to_file(
                    texte_to_save_to_mp3, file_name_mp3.lower() + ".mp3"
                )
                lire("terminé")
        else:
            print("rien à transformer")

    def replace_in_place(self, texte: str, index1: str, index2: str):
        """traduit sur place (remplacement) le texte sélectionné"""
        self.entree_prompt_principal.replace(chars=texte, index1=index1, index2=index2)

    def traduit_maintenant(self):
        """
        Translates the selected text or the entire text from the main prompt entry widget.
        This method performs the following steps:
        1. Sets a timer to measure the translation time.
        2. Retrieves the selected text from the main prompt entry widget.
        3. If there is selected text:
            a. Gets the start and end indices of the selected text.
            b. Processes the selected text.
            c. If the processed text is a list, translates each element and replaces the selected text with the translated text.
            d. If the processed text is not a list, translates the text and replaces the selected text with the translated text.
        4. If there is no selected text:
            a. Processes the entire text from the main prompt entry widget.
            b. If the processed text is a list, translates each element and concatenates the results.
            c. Calculates the translation time.
            d. Adds the translation result and timing information to the system.
            e. If the processed text is not a list, translates the text.
            f. Calculates the translation time.
            g. Adds the translation result and timing information to the system.
        5. Announces the end of the translation process.
        """
        self.set_timer(float(time.perf_counter_ns()))
        translated_text = self.entree_prompt_principal.get_selected()

        if translated_text is not None:
            indx1 = self.entree_prompt_principal.index(tk.SEL_FIRST)
            indx2 = self.entree_prompt_principal.index(tk.SEL_LAST)
            texte_traite = traitement_du_texte(str(translated_text))
            if isinstance(texte_traite, list):
                for element in texte_traite:
                    translated_text = str(translate_it(text_to_translate=element))
                    self.replace_in_place(
                        texte=translated_text,
                        index1=indx1,
                        index2=indx2,
                    )

            else:
                _result = str(translate_it(text_to_translate=texte_traite))
                self.replace_in_place(
                    texte=_result,
                    index1=indx1,
                    index2=indx2,
                )

        else:
            texte_traite = traitement_du_texte(self.entree_prompt_principal.get_text())

            if isinstance(texte_traite, list):
                sortie = str()
                for element in texte_traite:
                    translated_text = str(translate_it(text_to_translate=element))
                    sortie += "\n" + translated_text

                timing: float = (
                    time.perf_counter_ns() - self.get_timer()
                ) / TIMING_COEF
                self.addthing(
                    _timing=timing,
                    agent_appel=self.get_client(),
                    simple_text=self.entree_prompt_principal.get_text(),
                    ai_response=sortie,
                    model=self.get_model(),
                    submit_func=self.soumettre,
                )
            else:
                translated_text = str(translate_it(text_to_translate=texte_traite))
                timing: float = (
                    time.perf_counter_ns() - self.get_timer()
                ) / TIMING_COEF
                self.addthing(
                    _timing=timing,
                    agent_appel=self.get_client(),
                    simple_text=self.entree_prompt_principal.get_text(),
                    ai_response=translated_text,
                    model=self.get_model(),
                    submit_func=self.soumettre,
                )

        lire("fin de la traduction")

    def load_selected_model(self, evt: tk.Event):
        """
        Handles the event when a model is selected from the Listbox.

        Args:
            evt (tk.Event): The event object passed by Tkinter when an item is selected.

        Functionality:
            - Retrieves the selected index and value from the Listbox.
            - Prints the selected index and value.
            - Sets the model using the selected value.
            - Updates the text of a specific Button widget with the selected value.
            - Calls the `lire` function with the argument "ok".
            - If an exception occurs, prints an error message indicating no model was selected.
            - Finally, destroys the widget that currently has focus.

        Raises:
            Exception: If there is an error in retrieving the selected item or updating the widget.
        """
        # Note here that Tkinter passes an event object to onselect()
        w: tk.Listbox = evt.widget
        try:
            index = w.curselection()[0]
            value = w.get(index)
            print(YOU_SELECT_VALUE % (index, value))
            self.set_model(name_ia=str(value))
            _widget: tk.Button = self.nametowidget("cnvs1.cnvs2.btnlist")
            _widget.configure(text=value)
            lire("ok")
        except Exception as e:
            print(f"{e} : aucune ia sélectionner")
        finally:
            w.focus_get().destroy()  # type: ignore

    async def demander_actu(self, evt: tk.Event):
        """
        Handles the event when an item is selected from the Tkinter Listbox.
        This asynchronous method retrieves and processes RSS feed information based on the selected item in the Listbox.
        Args:
            evt (tk.Event): The event object passed by Tkinter, containing information about the Listbox selection event.
        Raises:
            Exception: If there is an issue retrieving or processing the RSS feed information, an error message is displayed, and the exception is logged and re-raised.
        Workflow:
            1. Retrieves the selected item's index and value from the Listbox.
            2. Finds the corresponding RSS feed content based on the selected value.
            3. Fetches the RSS feed information and processes each item.
            4. Uses an AI prompt to generate a summary for each RSS feed item.
            5. Updates the submission with the generated summaries.
            6. Displays the search results in the UI.
        """
        # Note here that Tkinter passes an event object to onselect()
        w: tk.Listbox = evt.widget
        feed_rss = []
        try:
            index = w.curselection()[0]

            value = str(w.get(index)).split(" :: ")[0]

            print('You selected item %d: "%s"' % (index, value))
            content_selected = [
                item["content"]
                for item in RULS_RSS
                if item["title"].lower() == value.lower()
            ].pop()

            feed_rss = recup_infos_rss_feed(
                content_selected=content_selected, value=value
            )
            if feed_rss.__len__():
                for item in feed_rss:
                    print(f"--> {item}")

                lire(f"Il y aura {len(feed_rss)} intitulés à récupérer")
                for i, subject in enumerate(feed_rss):
                    if subject.__len__():
                        kiki = await self.send_prompt(
                            content_discussion=make_resume(subject),
                            necessite_ai=True,
                            needed_groq=True,
                        )
                        self.set_submission(self.get_submission() + kiki)
                        # lire(f"Sujet {i}:   {str(subject)}")

                        time.sleep(4)

                lire("Récupération terminée")
                self.display_search_list_results(feed_rss)

        except Exception as e:
            error_msg = (
                f"Problème pour récupérer les infos (index:{index},value:{value})"
            )
            messagebox.showerror("OOps, ", error_msg)
            logger.exception(msg=error_msg, exc_info=e)
            logger.error("OOps, ", error_msg)
            raise e

    def lire_commande(self, evt: tk.Event):

        # Note here that Tkinter passes an event object to onselect()
        w: tk.Listbox = evt.widget
        index = w.curselection()[0]
        value = w.get(index)
        print('You selected item %d: "%s"' % (index, value))
        lire(value)

    def affiche_ia_list(self, list_to_check: list):
        """
        Display a list of AI you can use
        * affiche la listebox avec la liste donnée en paramètre list_to_check
        * click on it cause model AI to change
        """
        _listbox: tk.Listbox = self.traite_listbox(list_to_check)
        _listbox.bind(CLICK_LIST, func=self.load_selected_model)

    def display_history(self):
        """
        Display a list of AI you can use
        * affiche la listebox avec la liste donnée en paramètre list_to_check
        * click on it cause model AI to change
        """
        list_to_check = [element.split(".")[4:] for element in self.responses]
        _listbox: tk.Listbox = self.traite_listbox(list_to_check)

    def get_prompts_history(self) -> list:
        return self.prompts_history

    def supprimer_conversation(self, evt: tk.Event):
        conversation: Conversation = evt.widget
        print("Effacement de la conversation ::" + conversation.id + "::")
        try:
            self.responses.remove(conversation.id)
        except Exception as e:
            print(f"{e} ==> la fentre {conversation.id} est déjà effacée")
        conversation.destroy()
        conversation.canvas_edition.destroy()
        self.fenetre_scrollable.update()

    def addthing(
        self,
        _timing,
        agent_appel,
        simple_text: str,
        ai_response: str,
        model,
        submit_func,
    ):
        """
        Adds a conversation to the UI and history.
        Args:
            _timing (float): The timing information for the conversation.
            agent_appel (Any): The agent making the call.
            simple_text (str): The simple text input from the user.
            ai_response (str): The AI's response to the user's input.
            model (Any): The model to be used for the conversation.
            submit_func (Callable): The function to be called on submission.
        Returns:
            None
        """
        self.model = model
        fenetre_response: Conversation = Conversation(
            ai_response=ai_response,
            text=simple_text,
            master=self.fenetre_scrollable.frame,
            submit=submit_func,
            agent_appel=agent_appel,
            model_to_use=model,
            nb_conversation=self.responses.__len__(),
        )
        fenetre_response.pack(fill="x", expand=True)
        self.history.append(fenetre_response)

        self.responses.append(fenetre_response.id)

        this_thread: StoppableThread = StoppableThread(
            target=lambda: create_asyncio_task(
                async_function=self.save_to_history(
                    fenetre_response.id, simple_text, ai_response
                )
            )
        )
        this_thread.name = "save_to_history"
        this_thread.start()
        threads_outils.append(this_thread)

        fenetre_response.bind(
            "<Destroy>",
            func=self.supprimer_conversation,
        )

        fenetre_response.get_entree_response().insert_markdown(
            "_" + str(_timing)[:3] + "secondes < " + str(type(agent_appel)) + " >_\n",
        )
        fenetre_response.get_entree_response().insert_markdown(ai_response + "\n")

        fenetre_response.get_entree_question().insert_markdown(
            str(_timing)[:3] + "secondes < " + str(type(agent_appel)) + " >\n",
        )

        fenetre_response.get_entree_question().insert_markdown(simple_text + "\n")

        fenetre_response.affiche_fenetre_agrandie()

    def print_liste_des_conversations(self):
        """
        Prints a formatted list of conversations.

        This method prints out the conversation history in a formatted manner.
        It first prints the conversation history obtained from `get_prompts_history()`,
        displaying the prompt and response for each item. If the prompt or response
        is too long, it truncates them and adds ellipses.

        It then prints the current responses stored in `self.responses`,
        retrieving the prompt and response text from each `Conversation` widget.

        The output is divided into sections with asterisks and dashes for readability.
        """
        print("liste des conversations\n************************************")
        for item in self.get_prompts_history():
            print(
                item["fenetre_name"]
                + ":: \n-----------------------"
                + "\nPrompt:: "
                + str(
                    item["prompt"][:60] + "... "
                    if len(item["prompt"]) >= 59
                    else item["prompt"]
                )
                + RESPONSE
                + str(
                    item["response"][:59] + "...\n"
                    if len(item["response"]) >= 60
                    else item["response"] + "\n"
                )
            )
        print("************************************")
        for item in self.responses:
            suzi: Conversation = self.nametowidget(item)
            audrey = suzi.get_entree_question().get_text()
            julia = suzi.get_entree_response().get_text()
            print(
                suzi.widgetName
                + ":: \n-----------------------"
                + "\nPrompt:: "
                + str(audrey[:60] + "... " if len(audrey) >= 59 else audrey)
                + RESPONSE
                + str(julia[:59] + "...\n" if len(julia) >= 60 else julia + "\n")
            )
        print("************************************")
