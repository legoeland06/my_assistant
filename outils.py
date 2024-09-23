import asyncio
import io
import random
import subprocess
import threading
import time
from word2number import w2n
import webbrowser
import PyPDF2
from groq import Groq
from openai import ChatCompletion  # type: ignore
from PIL import Image, ImageTk

import pyaudio
import pyttsx3
import datetime
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from typing import Any, List, Tuple
import vosk
import ollama
from llama_index.llms.ollama import Ollama as Ola
import markdown
import requests
from Constants import (
    BYEBYE,
    DICT_NUMBERS,
    GOOGLECHROME_APP,
    INFOS_PROMPTS,
    LIENS_CHROME,
    MODEL_PATH,
    PREPROMPTS,
    PROMPTS_SYSTEMIQUES,
    RAPIDITE_VOIX,
    REQUEST_TIMEOUT_DEFAULT,
    RESUME_WEB,
    ROLE_TYPE,
    STARS,
    TEXTE_DEBRIDE,
    TEXTE_PREPROMPT_GENERAL,
    TIMING_COEF,
    TODAY_WE_ARE,
    WIDTH_TERM,
)
from StoppableThread import StoppableThread
import my_search_engine
from secret import NEWS_API_KEY

threads_outils = []
myengine:vosk.KaldiRecognizer=vosk.KaldiRecognizer(vosk.Model(MODEL_PATH, lang="fr-fr"), 16000)
mystream=pyaudio.PyAudio().open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16_000,
        input=True,
        frames_per_buffer=8_192,
    )


def initialise_conversation_audio() -> Tuple[bool, bool, str, str]:
    return True, False, "", ""


def make_resume(text: str) -> str:
    """
    En mode débridé. By removing redundant repetitions and events,
    Make a detailed and organized transcription of the content below:
    """
    return (
        """en mode débridé.
        By removing redundant repetitions and events, 
    Make a detailed and organized transcription of the content below:\n"""
        + text
        + """\n
NB: Be careful to archive key information as you will need it to continue a smooth conversation."""
    )


def lire_haute_voix(text: str):
    if threading.current_thread().getName() == "mode_veille":
        # on est déjà dans une thread donc inutile de surcharger ici
        # on peut se permettre de laissier finir une lecture avant de passer
        # à la suivante
        lecteur = pyttsx3.Engine()
        texte_reformate = (
        text.replace("**", " ")
        .replace("--", " ")
        .replace("+", " ")
        .replace("=", " ")
        .replace("#", " ")
        .replace("|", " ")
        .replace("/", " ")
        .replace(":", " ")
        .replace("https", " ")
    )
        lecteur.say(text=texte_reformate)
        lecteur.runAndWait()

    else:
        the_thread:StoppableThread = StoppableThread(
            target=lambda: create_asyncio_task(async_function=say_txt(text))
        )

        the_thread.name = "lire_haute_voix"
        the_thread.start()
        threads_outils.append(the_thread)
        if the_thread.ident and not the_thread.daemon:
            return True
        
        # _=create_asyncio_task(async_function=say_txt(text))
        # return True
        


def random_je_vous_ecoute() -> str:
    random_expression = [
        "...",
        "à vous",
        "je vous écoute",
        "je suis tout ouïe",
        "ok, ensuite",
        "dites moi maintenant",
        "... et?",
        "dacodac",
        "voila voila voila",
        "...",
    ]
    return random_expression[
        round(random.randint(0, random_expression.__len__() * 10) / 10)
        % random_expression.__len__()
    ]


def questionOuiouNon(
    question: str
) -> bool | str:
    lire_haute_voix(question)
    mystream.start_stream()

    while True:
        # engine.SetWords(enable_words=["oui", "non", "annulé"])
        if myengine.AcceptWaveform(
            mystream.read(
                num_frames=8192, exception_on_overflow=False
            )  # read in chunks of 4096 bytes
        ):  # accept waveform of input voice
            response = json.loads(myengine.Result())["text"].lower()
            if "annulé" in response:
                mystream.stop_stream()
                return "annulé"

            elif "oui" in response:
                mystream.stop_stream()
                return True

            elif "non" in response:
                mystream.stop_stream()
                return False


def questionOuverte(
    question: str
) -> str:
    lire_haute_voix(question)
    mystream.start_stream()
    while True:
        if myengine.AcceptWaveform(
            mystream.read(
                num_frames=8192, exception_on_overflow=False
            )  # read in chunks of 4096 bytes
        ):  # accept waveform of input voice
            response = str(json.loads(myengine.Result())["text"]).lower()
            if len(response.split()) >= 1:
                lire_haute_voix("merci")
                return response


async def say_txt(alire: str):
    """
    lit le texte passé en paramètre
    """
    texte_reformate = (
        alire.replace("*", " ")
        .replace("-", " ")
        .replace("+", " ")
        .replace("=", " ")
        .replace("#", " ")
        .replace("|", " ")
        .replace("/", " ")
        .replace(":", " ")
        .replace("https", " ")
    )
    lecteur = lecteur_init()
    if not lecteur._inLoop:
        lecteur.say(texte_reformate)
        lecteur.proxy.runAndWait()

    if lecteur._inLoop:
        lecteur.proxy.stop()

    return True


def from_rgb_to_tkColors(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    You must give a tuplet (r,g,b) like _from_rgb((125,125,125))"""
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


def read_text_file(file) -> list:
    """lit le fichier text chargé est passé en paramètre"""
    with open(file, "r", encoding="utf-8") as file_to_read:
        content = file_to_read.readlines()
    return content


def load_txt(parent):
    """
    Ouvre une boite de dialogue pour charger un fichier texte,
    appelle la méthode de lecture qui renvois le résultat
    sous forme de liste et retourne cette liste reformattée sous
    forme de texte
    """
    try:
        file_to_read = filedialog.askopenfile(
            parent=parent,
            title="Ouvrir un fichier txt",
            defaultextension="txt",
            mode="r",
            initialdir=".",
        )
        if file_to_read != None:
            print(file_to_read.name)

            resultat_txt = read_text_file(file_to_read.name)
            # lire_haute_voix("Fin de l'extraction")

            # on prepare le text pour le présenter à la méthode insert_markdown
            # qui demande un texte fait de lignes séparées par des \n
            # transforme list[str] -> str
            resultat_reformater = str().join(resultat_txt)

            return str(resultat_reformater)

    except:
        messagebox.Message("Problème avec ce fichier txt")
        return ""


def load_pdf(parent) -> str:
    try:
        file_to_read = filedialog.askopenfile(
            parent=parent,
            title="Ouvrir un fichier pdf",
            defaultextension="pdf",
            mode="r",
            initialdir=".",
        )
        lire_haute_voix("Extraction du PDF")
        if not file_to_read is None:
            resultat_txt = read_pdf(file_to_read.name)
            lire_haute_voix("Fin de l'extraction")
        else:
            resultat_txt = "rien à lire, fichier vide"
            lire_haute_voix(resultat_txt)

        return resultat_txt
    except:
        messagebox.Message("Problème avec ce fichier pdf")
        return "None"


def read_pdf(book: str):
    text = str()
    pdf_Reader = PyPDF2.PdfReader(book)
    pages = pdf_Reader.pages
    for page in pages:
        text += page.extract_text() + "\n"
    return text


def append_response_to_file(file_to_append, readable_ai_response):
    with open(file_to_append + ".html", "a", encoding="utf-8") as target_file:
        markdown_content = markdown.markdown(
            readable_ai_response, output_format="xhtml"
        )
        target_file.write(markdown_content + "\n")
    with open(file_to_append + ".md", "a", encoding="utf-8") as target_file:
        target_file.write("\n" + readable_ai_response + "\n")
    with open(file_to_append + ".txt", "a", encoding="utf-8") as target_file:
        markdown_content = readable_ai_response
        target_file.write(
            "::"
            + datetime.datetime.now().isoformat()
            + "::\n"
            + markdown_content
            + "\n"
        )


def append_saved_texte(file_to_append, readable_ai_response):
    with open(file_to_append + ".txt", "a", encoding="utf-8") as target_file:
        markdown_content = readable_ai_response
        target_file.write(
            "\n::"
            + datetime.datetime.now().isoformat()
            + "::\n"
            + markdown_content
            + "\n"
        )


def getEngine() -> vosk.KaldiRecognizer:
    """
    initialise le reconnaisseur vocal
    et retourne son instance
    """
    # initialise a voice recognizer
    lire_haute_voix("initialisation du micro")
    # if myengine.__init__:
    #     return myengine
    # rec = vosk.KaldiRecognizer(vosk.Model(MODEL_PATH, lang="fr-fr"), 16000)
    lire_haute_voix("micro initialisé")
    # set verbosity of vosk to NO-VERBOSE
    vosk.SetLogLevel(-1)
    # Initialize the model and return an instance
    return myengine


def getStream() -> pyaudio.Stream:
    return mystream
    # return pyaudio.PyAudio().open(
    #     format=pyaudio.paInt16,
    #     channels=1,
    #     rate=16_000,
    #     input=True,
    #     frames_per_buffer=8_192,
    # )


def traitement_du_texte(texte: str) -> list[Any | str]:
    """
    ### traitement_du_texte
    transforme le texte en liste de phrases
    ### RETURN : List
    """
    from nltk.tokenize import sent_tokenize

    liste_of_sent: List[str] = sent_tokenize(text=texte, language="french")

    if isinstance(liste_of_sent, list):
        liste_of_sentences = [
            sentence for sentence in liste_of_sent if len(sentence.split(" "))
        ]

        return liste_of_sentences
    return texte.splitlines()


def _traitement_du_texte(text: str, n: int) -> list:
    text_list: list = text.splitlines()
    return [text_list[i : i + n] for i in range(0, len(text_list), n)]


def getNewsApi(subject):
    """
    ### Récupére les titres du jour
    **_autour du subject_ donné en parametre de méthode**
    * Pour voir la forme de l'objet JSON, visitez : https://newsapi.org/
    """
    news_api = requests.request(
        "GET",
        "https://newsapi.org/v2/everything?q=" + subject +
        # + datetime.today().strftime("%d/%m/%Y, %H:%M:%S")
        "&searchin=title&domains=amnesty.org,972mag.com,linforme.com,afp.com,reuters.com,thenextweb,courrierinternational.com,lemonde.fr&sortBy=publishedAt&apiKey="
        + NEWS_API_KEY,
    )

    # lemonde = requests.request(
    #     "GET", "https://www.lemonde.fr/" + subject + "/rss_full.xml"
    # )

    return news_api


def splittextintochunks(text: str, maxcharsperchunk: int) -> list[str]:
    """
    Split a text into a list of chunks, each chunk being a string
    with a maximum length of `maxcharsperchunk` characters.

    Args:
        text (str): The text to split
        maxcharsperchunk (int): The maximum number of characters per chunk

    Returns:
        list[str]: A list of strings, each chunk being a string
                   with a maximum length of `maxcharsperchunk` characters
    """
    chunks = []
    currentchunk = str()

    for word in text.split():
        if len(currentchunk) + len(word) + 1 > maxcharsperchunk:
            chunks.append(currentchunk)
            currentchunk = word
        else:
            currentchunk += " " + word

    if currentchunk:
        chunks.append(currentchunk)

    return chunks


def reformateText(text: str, n: int) -> list[str]:
    reservoir = []
    for line in text.splitlines():
        if len(line) > n:
            reservoir.extend(splittextintochunks(line, n))
        else:
            reservoir.append(line)
    return reservoir


def translate_it(
    text_to_translate: str | list, initial: str = "auto", target: str = "fr"
) -> str:
    """
    traduit le text reçu par maximum de 500 caractères. Si le text est une liste,
    on la traduit une à une str
    @param text: desired text to translate, maximum de 500 caractères
    @return: str: translated text
    """

    # Use any translator you like, in this example GoogleTranslator
    from deep_translator import GoogleTranslator as _translator

    if text_to_translate is None:
        return ""

    if not isinstance(text_to_translate, str) and isinstance(text_to_translate, list):
        reformat_translated = " ".join(str(x) for x in text_to_translate)
    else:
        reformat_translated = text_to_translate

    translated = _translator(source=initial, target=target).translate(
        text=reformat_translated
    )  # output -> Weiter so, du bist großartig

    # print(translated)
    return translated


def actualise_index_html(texte: str, question: str, timing: float, model: str):
    if len(question) > 500:
        question = question[:499] + "..."
    with open("index" + ".html", "a", encoding="utf-8") as file_to_update:
        markdown_response = markdown.markdown(texte, output_format="xhtml")
        markdown_question = markdown.markdown(question, output_format="xhtml")
        file_to_update.write(
            "<div id='response_ai'>"
            + "<div id=question_to_ai>"
            + "<span class='btn btn-success'> "
            + model
            + "</span> "
            + "<span><strong>"
            + str(timing)
            + " secodnes "
            + "</strong></span>"
            + "<h3>Prompt</h3>"
            + markdown_question
            + "\n"
            + "</div>"
            + markdown_response
            + "\n"
            + "</div>"
        )


def create_asyncio_task(async_function):
    """
    méthode générique asynchrone
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(loop.create_task(async_function))
    loop.close()


def call_article_link(url):
    webbrowser.open_new(url)


async def downloadimage(url_or_path: str, taille: int) -> ImageTk.PhotoImage | None:
    try:
        image_bytes = url_or_path
        if "http" in url_or_path:
            response = requests.get(url_or_path + "?raw=true")  #  tester url
            image_bytes = io.BytesIO(response.content)

        with Image.open(fp=image_bytes, mode="r") as img:
            kikispec = ImageTk.PhotoImage(
                image=img.resize(
                    (taille, int(taille * (float(img.height) / float(img.width))))
                )
            )
            return kikispec
    except:
        return None


def chargeImage(filename: str, taille: int):
    img = Image.open(filename)
    return ImageTk.PhotoImage(
        image=img.resize((taille, int(taille * (float(img.height) / float(img.width)))))
    )


def lire_text_from_object(object: Any):
    try:
        texte_to_talk = object.get(tk.SEL_FIRST, tk.SEL_LAST)
    except:
        texte_to_talk = object.get("1.0", tk.END)
    finally:
        lire_haute_voix(texte_to_talk)


def get_pre_prompt(rubrique: str, prompt_name: str):
    return PROMPTS_SYSTEMIQUES[rubrique].replace(rubrique, prompt_name)


def lire_ligne(evt: tk.Event):
    widget_to_read: tk.Listbox = evt.widget
    say_txt(
        str(
            widget_to_read.get(
                widget_to_read.curselection(), widget_to_read.curselection() + 1
            )
        )
    )  # type: ignore


def textToNumber(text: str) -> int:
    for item in DICT_NUMBERS:
        if item["letter"] in text.lower():
            return item["number"]
    return 10


def lecteur_init():
    """
    ## initialise le Lecteur de l'application
    * initialise pyttsx3 avec la langue française
    * set la rapidité de locution.
    #### RETURN : lecteur de type Any|Engine
    """
    lecteur = pyttsx3.init()
    lecteur.setProperty("lang", "french")
    lecteur.setProperty("rate", RAPIDITE_VOIX)

    return lecteur


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


def lancer_search_chrome(word_to_search: str) -> subprocess.Popen[str]:
    link_search = "https://www.google.fr/search?q="

    return subprocess.Popen(
        GOOGLECHROME_APP + link_search + word_to_search,
        text=True,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def tester_appelation(appelation: str) -> str | None:
    for name, link in LIENS_CHROME.items():
        if name in appelation:
            _pid = lancer_chrome(url=link)
            return link


def lire_fichier(file_name: str) -> str:

    with open(file_name + ".txt", "r", encoding="utf-8") as file:
        if file.readable():
            data_file = file.read().rstrip()
            return "fais moi un résumé de ce texte: " + data_file
        else:
            return ""


def lire_url(url: str) -> str:
    return url


def merci_au_revoir(
    lecteur: pyttsx3.Engine,
    stream_to_stop: pyaudio.Stream,
):
    # Stop and close the stream_to_stop
    lecteur.say(BYEBYE, False)
    lecteur.stop()
    stream_to_stop.stop_stream()
    stream_to_stop.close()
    au_revoir()


def au_revoir():
    exit(0)


def get_groq_ia_list(api_key):
    sortie = []
    url = "https://api.groq.com/openai/v1/models"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    for item in response.json()["data"]:
        sortie.append(item["id"])
    print(str(sortie))
    return sortie


def ask_to_resume(agent_appel, prompt: str, model_to_use):

    ai_response, _timing = ask_to_ai(
        agent_appel=agent_appel,
        prompt=make_resume(prompt),
        model_to_use=model_to_use,
        motcle=str(),
        p_history=str(),
    )

    return str(ai_response)


def letters_to_number(letters: str, lang: str = "fr") -> int | bool:
    try:
        result = w2n.word_to_num(translate_it(letters, initial="fr", target="en"))
        return int(result)
    except:
        return False


def websearching(term: str):
    """
    ### make a litle web-search

    récupérer le mot dans le prompt directement
    en isolant la ligne et en récupérant tout ce qu'il y a après
    avoir identifier les mots clés "recherche web : "
    expression_found = (term.split(" : ")[1]).replace(" ", "+")
    resultat_de_recherche = str(self.lancer_chrome(expression_found))

    on execute cette recherche sur le web
    avec l'agent de recherche search.main()
    """

    # TODO : récupérer le mot dans le prompt directement
    # en isolant la ligne et en récupérant tout ce qu'il y a après
    # avoir identifier les mots clés "recherche web : "
    expression_found = (term.split(" : ")[1]).replace(" ", "+")
    # resultat_de_recherche = str(lancer_chrome(expression_found))

    # on execute cette recherche sur le web
    # avec l'agent de recherche search.main()
    lire_haute_voix("recherche web " + term.split(" : ")[1])
    search_results: list = my_search_engine.main(expression_found)

    goodlist = "\n".join(
        [
            str(element["snippet"] + "\n" + element["formattedUrl"] + "\n")
            for element in search_results
        ]
    )
    return goodlist


def check_content(content: str, client, model_to_use) -> tuple:
    """
    content (str) : content to check

    str : content augmented with potentialy web-searches
    bool : isAskToDebride wich notify to débride AI
    float : timing
    Exemple :
        >>> a, b, c = check_content(content)"""
    time0 = time.perf_counter_ns()
    result_recherche = []
    isAskToDebride = False
    for line in [line for line in content.splitlines() if line.strip()]:
        # si on a trouvé la phrase << rechercher sur le web : >>
        if "rechercher sur le web : " in line:
            goodlist = websearching(line)

            # TODO : PAS SUR DE l'UTILITE
            super_result, _ = ask_to_ai(
                client, goodlist, model_to_use, motcle=str(), p_history=str()
            )

            result_recherche.append(
                {
                    "resultat_de_recherche": line.split(" : ")[1]
                    + "\n"
                    + str(super_result)
                }
            )

            bonne_liste = "Recherche sur le Web : \n"
            for recherche in [
                element["resultat_de_recherche"] for element in result_recherche
            ]:
                bonne_liste += recherche + "\n\n"

            content += "\nRésultat des recherches : \n" + str(
                bonne_liste if len(str(recherche)) else ""
            )

        # si on a trouvé la phrase << en mode débridé >>
        if not isAskToDebride and "en mode débridé" in line:
            isAskToDebride = True

    timing: float = (time.perf_counter_ns() - time0) / TIMING_COEF

    return content, isAskToDebride, timing


def ask_to_ai(agent_appel, prompt: str, model_to_use, motcle, p_history) -> tuple:
    letexte, isAskToDebride, timing = check_content(
        content=prompt, client=agent_appel, model_to_use=model_to_use
    )
    time0 = time.perf_counter_ns()
    if isinstance(agent_appel, ollama.Client):
        try:
            llm: ollama.Client = agent_appel.chat(  # type: ignore
                model=model_to_use,
                messages=[
                    {
                        "role": "user",
                        "content": str(letexte),
                        "num_ctx": 2048,
                        "num_predict": 40,
                        "keep_alive": -1,
                    },
                ],  # type: ignore
            )
            ai_response = llm["message"]["content"]  # type: ignore

        except ollama.RequestError as requestError:
            print("OOps aucun model chargé : ", requestError)
        except ollama.ResponseError as responseError:
            print("OOps la requête ne s'est pas bien déroulée", responseError)
    elif isinstance(agent_appel, Groq):

        this_message = [
            {
                "role": "system",
                "content": (
                    TEXTE_DEBRIDE
                    if isAskToDebride
                    else (
                        TEXTE_PREPROMPT_GENERAL
                        + (
                            ("\nYou are an expert in : " + str(motcle))
                            if len(str(motcle).strip())
                            else ""
                        )
                    )
                ),
            },
            {
                "role": "assistant",
                "content": TODAY_WE_ARE
                + (
                    # prend tout l'historique des prompts
                    str(p_history)
                    if len(str(p_history))
                    else ""
                ),
            },
            {
                "role": "user",
                "content": letexte,
            },
        ]

        try:
            llm: ChatCompletion = agent_appel.chat.completions.create(  # type: ignore
                messages=this_message,
                model=model_to_use,
                temperature=1,
                max_tokens=4060,
                # response_format="{type:jsonformat}"
                n=1,
                function_call="auto",
                stream=False,
                stop=None,
                timeout=10,
            )

            ai_response = llm.choices[0].message.content  # type: ignore

        except:
            messagebox.Message("OOps, ")

    elif isinstance(agent_appel, Ola.__class__):
        try:
            llm: Ola = agent_appel(
                base_url="http://localhost:11434",
                model=model_to_use,
                request_timeout=REQUEST_TIMEOUT_DEFAULT,
                additional_kwargs={
                    "num_ctx": 2048,
                    "num_predict": 40,
                    "keep_alive": -1,
                },
            )

            ai_response = llm.chat(letexte).message.content

        except:
            messagebox.Message("OOps, ")

    # TODO
    try:
        # calcul le temps écoulé
        timing: float = timing + (time.perf_counter_ns() - time0) / TIMING_COEF
        print(ai_response)
        append_response_to_file(RESUME_WEB, ai_response)
        actualise_index_html(
            texte=str(ai_response),
            question=letexte,
            timing=timing,
            model=model_to_use,
        )

        return ai_response, timing
    except:
        print("problème de de délais de réponse")
        return "problème de délais de réponse", timing


def askToAi(agent_appel, prompt, model_to_use) -> tuple:

    time0 = time.perf_counter_ns()

    if isinstance(agent_appel, ollama.Client):
        try:
            llm: ollama.Client = agent_appel.chat(  # type: ignore
                model=model_to_use,
                messages=[
                    {
                        "role": ROLE_TYPE,  # type: ignore
                        "content": prompt,
                        "num_ctx": 4096,
                        "num_predict": 40,
                        "keep_alive": -1,
                    },
                ],
            )
            ai_response = llm["message"]["content"]  # type: ignore
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

    # calcul le temps écoulé
    timing: float = (time.perf_counter_ns() - time0) / 1_000_000_000.0
    print(ai_response)
    print("Type_agent_appel::" + str(type(agent_appel)))
    print("Type_ai_réponse::" + str(type(ai_response)))

    append_response_to_file(RESUME_WEB, ai_response)
    actualise_index_html(
        texte=str(ai_response), question=prompt, timing=timing, model=model_to_use
    )

    return ai_response, timing
