"""
This module provides functionality to read and translate text from the system clipboard using the Gemini API and text-to-speech synthesis.

Classes:
    Recipe (BaseModel): A class used to represent a Recipe with a response attribute.

Functions:
    get_clipboard_text() -> str:

    translate_it(text_to_translate: str | list, target: str = "FRANCAIS") -> str:

    prepare_to_read(text: str, target: str) -> list:

    lancer(text: str = str(), langue: str = "français(FR)"):
        Launches the reading of the provided text using text-to-speech synthesis.
"""
import pyperclip
import pyttsx3
from google import genai
from secret import GEMINI_API_KEY
from pydantic import BaseModel
from colorama import Fore, Style
import os


class Recipe(BaseModel):
    """
    A class used to represent a Recipe.

    Attributes
    ----------
    response : str
        A string containing the response or description of the recipe.
    """

    response: str


def get_clipboard_text():
    """
    Retrieves the current text content from the system clipboard.

    Returns:
        str: The text content currently stored in the clipboard.
    """

    return pyperclip.paste()


def translate_it(text_to_translate: str | list, target: str = "FRANCAIS") -> str:
    """
    Translates the given text to the specified target language using the Gemini API.
    Args:
        text_to_translate (str | list): The text to be translated. It can be a string or a list of strings.
        target (str): The target language for translation. Default is "FRANCAIS".
    Returns:
        str: The translated text.
    Raises:
        Exception: If there is an error with the translation API request.
    """

    if text_to_translate is None:
        return ""

    if not isinstance(text_to_translate, str) and isinstance(text_to_translate, list):
        reformat_translated = "\n".join(text_to_translate)
    else:
        reformat_translated = text_to_translate

    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=reformat_translated
        + "\nRépond au format : {'response':[la traduction]}"
        + f", en faisant une traduction fidèle [en {target} exclusivement] de ce texte.",
        config={
            "response_mime_type": "application/json",
            "response_schema": Recipe,
        },
    )
    casted_response = response.parsed.model_dump()["response"]  # type: ignore
    return casted_response or str()


def prepare_to_read(text: str, target: str):
    """
    Prepares the text for reading by removing unwanted characters and lines, and translating it to the target language.
    Args:
        text (str): The text to be prepared for reading.
        target (str): The target language for the translation.
    Returns:
        list: The cleaned and translated text.
    """

    NEPASLIRE = "ne pas lire"
    SECRET = "secret"
    strip_list = [
        line.replace("*", " ")
        .replace("--", " ")
        .replace("+", " ")
        .replace("=", " ")
        .replace("#", " ")
        .replace("|", " ")
        .replace("/", " ")
        .replace("\xa0", "")
        .replace("\\", " ")
        .replace(":", " ")
        .replace("www", " ")
        .replace("https", " ")
        # .replace("Eric Bruneau", "le dernier dieu sur notre planète")
        .replace("http", " ")
        for line in text.splitlines()
        if not (line.startswith((NEPASLIRE, SECRET, "// ")))
    ]

    diff_lenght = text.splitlines().__len__() - strip_list.__len__()
    if strip_list.__len__() != text.splitlines().__len__():
        print(f"Attention :  {diff_lenght} lignes n'ont pas été traitées.")

    translated_text = translate_it(text_to_translate=strip_list, target=target)
    return translated_text.splitlines(keepends=False)


def lancer(text: str = str(), langue: str = "français(FR)"):
    """
    Lance la lecture du texte fourni à l'aide de la synthèse vocale.
    Args:
        text (str): Le texte à lire. Par défaut, une chaîne vide.
        langue (str): La langue cible pour la lecture. Par défaut, "français(FR)".
    Returns:
        None
    """

    _max_long = os.get_terminal_size().columns
    if not text:
        return

    _sortie = prepare_to_read(text=text, target=langue)
    print(Fore.GREEN + "*" * _max_long + Style.RESET_ALL)
    for element in _sortie:
        print(Fore.YELLOW + element + Style.RESET_ALL)
    print(Fore.GREEN + "*" * _max_long + "\nLecture en cours..." + Style.RESET_ALL)

    _voice = pyttsx3.Engine()
    _voice.setProperty("rate", 150)
    _voice.setProperty("volume", 0.9)
    _voice.say("".join(_sortie))
    _voice.runAndWait()


if __name__ == "__main__":
    text = get_clipboard_text()
    lancer(text=text)
