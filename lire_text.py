"""
This script retrieves text from the system clipboard, translates it to French using the Google GenAI API,
cleans the translated text by removing certain unwanted characters and lines, and then reads the cleaned text aloud.
Modules:
    pyperclip: A cross-platform Python module for clipboard operations.
    pyttsx3: A text-to-speech conversion library in Python.
    google.genai: A module for interacting with the Google GenAI API.
    secret: A module to store secret keys.
    pydantic: A data validation and settings management library.
Classes:
    Recipe(BaseModel): A Pydantic model for the API response.
Functions:
    get_clipboard_text():
    translate_it(text_to_translate: str | list, initial: str = "français", target: str = "français") -> str:
    prepare_to_read(text: str) -> list:
Usage:
    Run the script to retrieve text from the clipboard, translate it, clean it, and read it aloud.
"""

import pyperclip
import pyttsx3
from google import genai
from secret import GEMINI_API_KEY
from pydantic import BaseModel


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
    Retrieves the current text from the system clipboard.
    Returns:
        str: The text currently stored in the clipboard.
    """

    # Récupérer le texte du presse-papiers
    clipboard_text = pyperclip.paste()

    # Retourner le texte récupéré
    return clipboard_text


def translate_it(
    text_to_translate: str | list, initial: str = "français", target: str = "français"
) -> str:
    """
    Translates the given text from the initial language to the target language using the Google GenAI API.
    Args:
        text_to_translate (str | list): The text to be translated. Can be a string or a list of strings.
        initial (str, optional): The initial language of the text. Defaults to "français".
        target (str, optional): The target language for the translation. Defaults to "français".
    Returns:
        str: The translated text.
    Raises:
        ValueError: If text_to_translate is neither a string nor a list.
    """

    if text_to_translate is None:
        return ""

    if not isinstance(text_to_translate, str) and isinstance(text_to_translate, list):
        reformat_translated = " ".join(str(x) for x in text_to_translate)
    else:
        reformat_translated = text_to_translate

    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=reformat_translated
        + "\nRépond au format : {'response':[la traduction]}"
        + f", en faisant une traduction fidèle en {target} de ce texte.",
        config={
            "response_mime_type": "application/json",
            "response_schema": Recipe,
        },
    )
    # translated = _translator(source=initial, target=target).translate(
    #     text=reformat_translated
    casted_response = response.parsed.model_dump()["response"]  # type: ignore
    return str(casted_response) or str()


def prepare_to_read(text: str):
    """
    Prepares the given text for reading by translating it to French and removing certain unwanted characters and lines.
    Args:
        text (str): The text to be prepared and translated.
    Returns:
        list: A list of strings representing the cleaned and translated lines of text.
    Notes:
        - The text is translated to French using the `translate_it` function.
        - Lines containing "ne pas lire", "secret", or starting with "// " are excluded.
        - Certain characters such as "*", "--", "+", "=", "#", "|", "/", "\\", ":", "www", "https", and "http" are replaced with spaces.
        - The name "Eric Bruneau" is replaced with "le dernier dieu sur notre planète :-)".
        - If any lines are excluded, a message is printed indicating the number of lines that were not read.
    """

    translated_text = translate_it(text_to_translate=text, target="français")
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
        .replace("\\", " ")
        .replace(":", " ")
        .replace("www", " ")
        .replace("https", " ")
        .replace("Eric Bruneau", "le dernier dieu sur notre planète")
        .replace("http", " ")
        for line in translated_text.splitlines()
        if not (line.startswith((NEPASLIRE, SECRET, "// ")))
    ]

    diff_lenght = translated_text.splitlines().__len__() - strip_list.__len__()
    if strip_list.__len__() != translated_text.splitlines().__len__():
        print(f"Attention :  {diff_lenght} lignes n'ont pas été lues")

    return strip_list


if __name__ == "__main__":

    text = get_clipboard_text()
    real_text = prepare_to_read(text).__repr__()
    print(real_text + "\nLecture en cours...")
    lecteur = pyttsx3.Engine()
    lecteur.setProperty("rate", 150)
    lecteur.setProperty("volume", 0.9)
    lecteur.say(real_text)
    lecteur.runAndWait()
