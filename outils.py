import asyncio
import subprocess
from threading import Thread
from groq import Groq
from openai import ChatCompletion

import my_search_engine as search
import pyaudio
import pyttsx3
import datetime
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import tkinter.font as tkfont
from typing import Any, List, Mapping, Tuple
import imageio.v3 as iio
import PyPDF2
import markdown
import requests
from Constants import (
    BYEBYE,
    DARK3,
    GOOGLECHROME_APP,
    INFOS_PROMPTS,
    LIENS_CHROME,
    LIGHT3,
    PREPROMPTS,
    PROMPTS_SYSTEMIQUES,
    RAPIDITE_VOIX,
    ROLE_USER,
    STARS,
    TEXTE_DEBRIDE,
    TODAY_WE_ARE,
    TRAITEMENT_EN_COURS,
    WIDTH_TERM,
)
from SimpleMarkdownText import SimpleMarkdownText
from secret import GROQ_API_KEY


def initialise_conversation_audio() -> Tuple:
    return True, False, "", ""


def make_resume(text: str) -> str:
    return (
        "En supprimant les répétitions et événements redondants, fais une retranscrition détaillée et organisée du contenu ci-dessous:\n"
        + text
    )


def thread_lecture(text: str):
    _the_thread = Thread(
        None,
        name="the_thread",
        target=lambda: loop_lecture(
            # nettoyage sommaire du texte
            text=nettoyage_sommaire(text)
        ),
    ).start()


def nettoyage_sommaire(text: str):
    return (
        text.replace("*", " ")
        .replace("-", " ")
        .replace("=", " ")
        .replace("#", " ")
        .replace("|", " ")
        .replace("/", " ")
        .replace(":", " ")
        .replace("https", " ")
    )


def petite_recherche(term: str):
    # TODO : récupérer le mot dans le prompt directement
    # en isolant la ligne et en récupérant tout ce qu'il y a après
    # avoir identifier les mots clés "recherche web : "
    expression_found = (term.split(" : ")[1]).replace(" ", "+")

    # on execute cette recherche sur le web
    # avec l'agent de recherche search.main()
    thread_lecture("recherche web " + term.split(" : ")[1])
    search_results: list = search.main(expression_found)

    goodlist = "\n".join(
        [
            str(element["snippet"] + "\n" + element["formattedUrl"] + "\n")
            for element in search_results
        ]
    )
    return goodlist


def check_content(content: str):
    """
    ### check the content
    Verify some keywords like :
        << rechercher sur le web : >>
        << en mode débridé >>

        @param: content type str

        @return: content type str ,
        @return: isAskToDebride type bool,
        @return: timing type float
    """
    result_recherche = []
    isAskToDebride = False
    for line in [line for line in content.splitlines() if line.strip()]:
        # si on a trouvé la phrase << rechercher sur le web : >>
        if "rechercher sur le web : " in line:

            goodlist = petite_recherche(line)

            result_recherche.append(
                {
                    "resultat_de_recherche": line.split(" : ")[1]
                    + "\n"
                    + "".join(goodlist)
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

        if not isAskToDebride and "en mode débridé" in line:
            isAskToDebride = True

    return content, isAskToDebride


def loop_lecture(text: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(lecture_texte(text=text))
    loop.run_forever()


async def lecture_texte(text: str):
    """
    lit le texte passé en paramètre
    """

    lecteur = engine_lecteur_init()
   
    if not lecteur._inLoop:
        lecteur.say(text)
        lecteur.runAndWait()
        lecteur.stop()


def from_rgb_to_tkColors(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    You must give a tuplet (r,g,b) like _from_rgb((125,125,125))"""
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


def bold_it(obj: tk.Text | SimpleMarkdownText):
    return tkfont.Font(**obj.configure())


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
        print(file_to_read.name)
        resultat_txt = read_text_file(file_to_read.name)
        lecture_texte("Fin de l'extraction")

        # on prepare le text pour le présenter à la méthode insert_markdown
        # qui demande un texte fait de lignes séparées par des \n
        # transforme list[str] -> str
        resultat_reformater = "".join(resultat_txt)
        return resultat_reformater

    except:
        messagebox("Problème avec ce fichier txt")
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
        lecture_texte("Extraction du PDF")
        resultat_txt = read_pdf(file_to_read.name)
        lecture_texte("Fin de l'extraction")
        return resultat_txt
    except:
        messagebox("Problème avec ce fichier pdf")
        return None


def read_pdf(book):
    text = ""
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
        target_file.write(
            "\n=============================="
            + "\n==============================\n\n"
            + readable_ai_response
            + "\n"
        )
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


def traitement_du_texte(texte: str, number: int) -> list[list[str]]:
    """
    ### traitement_du_texte
    #### si le texte possède plus de <number> caractères :
        on coupe le texte en plusieurs listes de maximum <number> caractères
        et on renvois cette liste de liste
    #### sinon :
        on envois le texte telquel

    ### RETURN : str ou List
    """
    from nltk.tokenize import sent_tokenize, word_tokenize

    liste_of_sent: List[str] = sent_tokenize(text=texte)

    liste_of_sentences = [
        sentence for sentence in liste_of_sent if len(sentence.split(" ")) <= number
    ]

    return liste_of_sentences


def translate_it(text_to_translate: str) -> str:
    """
    traduit le text reçu par maximum de 500 caractères. Si le text est une liste,
    on la traduit une à une str
    @param text: desired text to translate, maximum de 500 caractères
    @return: str: translated text
    """

    # Use any translator you like, in this example GoogleTranslator
    from deep_translator import GoogleTranslator as _translator

    if not isinstance(text_to_translate, str):
        reformat_translated = " ".join(str(x) for x in text_to_translate)
    else:
        reformat_translated = text_to_translate

    translated = _translator(source="auto", target="fr").translate(
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


def lire_text_from_object(object: SimpleMarkdownText | tk.Text | tk.Listbox):
    try:
        texte_to_talk = object.get_selection()
    except:
        texte_to_talk = object.get_text()
    finally:
        lecture_texte(texte_to_talk) if texte_to_talk != "" else None


def get_pre_prompt(rubrique: str, prompt_name: str):
    return PROMPTS_SYSTEMIQUES[rubrique].replace(rubrique, prompt_name)


def close_infos_model(button: tk.Button, text_area: SimpleMarkdownText):
    button.destroy()
    text_area.destroy()


def lire_ligne(evt: tk.Event):
    widget_to_read: tk.Listbox = evt.widget
    lecture_texte(
        str(
            widget_to_read.get(
                widget_to_read.curselection(), widget_to_read.curselection() + 1
            )
        )
    )


def display_infos_model(master: tk.Canvas, content: Mapping[str, Any]):
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=8)
    canvas_bouton_minimize = tk.Frame(master=master, bg=from_rgb_to_tkColors(DARK3))
    canvas_bouton_minimize.pack(fill="x", expand=True)
    infos_model = SimpleMarkdownText(master, font=default_font)
    bouton_minimize = tk.Button(
        canvas_bouton_minimize,
        text="-",
        command=lambda: close_infos_model(
            button=canvas_bouton_minimize, text_area=infos_model
        ),
        fg=from_rgb_to_tkColors(DARK3),
        bg="red",
    )
    bouton_minimize.pack(side=tk.RIGHT)
    infos_model.configure(
        background=from_rgb_to_tkColors(DARK3),
        fg=from_rgb_to_tkColors(LIGHT3),
        height=11,
    )
    print("okok")
    jsonified = (
        json.dumps(
            content["details"],
            indent=4,
        )
        + "\n"
    )

    print(jsonified)
    infos_model.pack(fill="x", expand=True)
    infos_model.insert_markdown(mkd_text=jsonified)


def engine_lecteur_init():
    """
    ## initialise le Lecteur de l'application
    * initialise pyttsx3 avec la langue française
    * set la rapidité de locution.
    #### RETURN : lecteur de type Any|Engine
    """
    lecteur = pyttsx3.init()
    lecteur.setProperty("lang", "french")
    lecteur.setProperty('voice','com.apple.speech.synthesis.voice.fiona')
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


def tester_appellation(appelation: str) -> str:
    for lien in LIENS_CHROME:
        if lien in appelation:
            chrome_pid = lancer_chrome(url=LIENS_CHROME[lien])
            return lien


def lire_fichier(file_name: str) -> str:

    with open(file_name + ".txt", "r", encoding="utf-8") as file:
        if file.readable():
            data_file = file.read().rstrip()
            return "fais moi un résumé de ce texte: " + data_file
        else:
            return ""


def lire_url(url: str) -> str:
    return url


def lire_image(name: str) -> any:
    # Load a single image
    im = iio.imread(name)
    print(im.shape)  # Shape of the image (height, width, channels)
    return im


def veullez_patienter(moteur_de_diction):
    moteur_de_diction(TRAITEMENT_EN_COURS, stop_ecoute=True)


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


def ask_to_resume(agent_appel, prompt, model_to_use):

    if isinstance(agent_appel, Groq):

        this_message = [
            {
                "role": ROLE_USER,
                "content": str(prompt)
                + "\n Instruction: faire un résumé de toutes les conversations ci-dessus en un prompt concentré",
            },
        ]

        try:
            llm: ChatCompletion = agent_appel.chat.completions.create(
                messages=this_message,
                model=model_to_use,
                temperature=1,
                max_tokens=4060,
                n=1,
                stream=False,
                stop=None,
                timeout=10,
            )

            ai_response = llm.choices[0].message.content
        except:
            messagebox.Message("OOps, ")
    else:
        messagebox.Message("Ne fonctionne qu'avec groq")

    return ai_response


def askToAi(prompt: str, model_to_use) -> Any:

    final_text, isAskToDebride = check_content(prompt)
    this_message = [
        {
            "role": ROLE_USER,
            "content": TODAY_WE_ARE
            + (TEXTE_DEBRIDE if isAskToDebride else "")
            + final_text
            + "\n Instruction: ",
        },
    ]

    try:
        llm: ChatCompletion = Groq(api_key=GROQ_API_KEY).chat.completions.create(
            messages=this_message,
            model=model_to_use,
            temperature=1,
            max_tokens=4060,
            n=1,
            stream=False,
            stop=None,
            timeout=10,
        )

        ai_response = llm.choices[0].message.content
    except:
        messagebox.Message("OOps, ")

    return ai_response
