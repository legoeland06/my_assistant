import pyttsx3
import datetime
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import tkinter.font as tkfont
from typing import Any, Mapping

import PyPDF2
import markdown
from Constants import DARK3, LIGHT3, PROMPTS_SYSTEMIQUES, RAPIDITE_VOIX
from SimpleMarkdownText import SimpleMarkdownText


def say_txt(alire: str):
    """
    lit le texte sans passer par un thread
    """
    lecteur = engine_lecteur_init()
    lecteur.say(alire)
    lecteur.runAndWait()
    lecteur.stop()


def from_rgb_to_tkColors(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    You must give a tuplet (r,g,b) like _from_rgb((125,125,125))"""
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


def bold_it(obj: tk.Text | SimpleMarkdownText):
    return tkfont.Font(**obj.configure())


def read_prompt_file(file):
    with open(file, "r", encoding="utf-8") as file_to_read:
        content = file_to_read.readlines()
    return content


def load_txt(parent):
    try:
        file_to_read = filedialog.askopenfile(
            parent=parent,
            title="Ouvrir un fichier txt",
            defaultextension="txt",
            mode="r",
            initialdir=".",
        )
        print(file_to_read.name)
        resultat_txt = read_prompt_file(file_to_read.name)
        say_txt("Fin de l'extraction")

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
        say_txt("Extraction du PDF")
        resultat_txt = read_pdf(file_to_read.name)
        say_txt("Fin de l'extraction")
        # self.entree_prompt_principal.insert_markdown(mkd_text=resultat_txt)
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
        markdown_content = markdown.markdown(
            readable_ai_response, output_format="xhtml"
        )
        target_file.write(markdown_content + "\n")
    with open(file_to_append + ".txt", "a", encoding="utf-8") as target_file:
        markdown_content = readable_ai_response
        target_file.write(
            "::"
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
    # on découpe le texte par mots
    liste_of_words = texte.split()
    if len(liste_of_words) >= number:
        list_of_large_text: list[list[str]] = []
        new_list: list[str] = []
        counter = 0
        for word in liste_of_words:
            counter += len(word) + 1
            new_list.append(word)
            if counter >= number:
                list_of_large_text.append(new_list)
                new_list = []
                counter = 0
        return list_of_large_text
    else:
        return texte


def translate_it(text_to_translate: str) -> str:
    """
    traduit le text reçu par maximum de 500 caractères. Si le text est une liste, on la traduit une à une str
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


def lire_text_from_object(object: tk.Text):
    texte_to_talk = object.get("1.0", tk.END)

    if texte_to_talk != "":
        try:
            texte_to_talk = object.get(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            texte_to_talk = object.get("1.0", tk.END)
        finally:
            say_txt(texte_to_talk)
            return texte_to_talk


def get_pre_prompt(rubrique: str, prompt_name: str):
    return PROMPTS_SYSTEMIQUES[rubrique].replace(rubrique, prompt_name)


def close_infos_model(button: tk.Button, text_area: SimpleMarkdownText):
    button.destroy()
    text_area.destroy()


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
    lecteur.setProperty("rate", RAPIDITE_VOIX)

    # TODO Rien à faire ici, voir si on peut le déplacer
    pyttsx3.speak("lancement...")

    return lecteur
