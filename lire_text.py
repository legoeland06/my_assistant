import pyperclip
import pyttsx3
from secret import GEMINI_API_KEY
from pydantic import BaseModel


class Recipe(BaseModel):
    response:str

def get_clipboard_text():
    """
    Récupère le texte actuellement présent dans le presse-papiers.

    Returns:
        str: Le texte récupéré du presse-papiers.
    """
    # Récupérer le texte du presse-papiers
    clipboard_text = pyperclip.paste()

    # Retourner le texte récupéré
    return clipboard_text


def translate_it(
    text_to_translate: str | list, initial: str = "français", target: str = "français"
) -> str:

    from google import genai

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
        + "\nRépond au format : {'response':[la traduction]}"+f", en faisant une traduction fidèle en {target} de ce texte.",
        config={
            "response_mime_type": "application/json",
            "response_schema": Recipe,
        },
    )
    # translated = _translator(source=initial, target=target).translate(
    #     text=reformat_translated
    casted_response=response.parsed.model_dump()["response"] # type: ignore
    return str(casted_response) or str()


def prepare_to_read(text: str):
    """
    Prépare un texte pour être lu en effectuant une traduction et en supprimant certaines lignes indésirables.

    Args:
        text (str): Le texte à préparer pour la lecture.

    Returns:
        list: Une liste de lignes de texte prêtes à être lues, après traduction et suppression des lignes indésirables.

    Notes:
        - Le texte est d'abord traduit en français à l'aide de la fonction `translate_it`.
        - Les lignes commençant par "ne pas lire", "secret", ou "// " sont supprimées.
        - Les caractères spéciaux tels que "*", "--", "+", "=", "#", "|", "/", ":", et "https" sont remplacés par des espaces.
        - Si des lignes sont supprimées, un message d'avertissement est affiché indiquant le nombre de lignes non lues.
    """
    translated_text = translate_it(text_to_translate=text,target="français")
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
    """
    Point d'entrée principal du script.

    Ce bloc de code est exécuté uniquement lorsque le fichier est exécuté directement (et non importé).
    Il récupère le texte du presse-papiers, le prépare pour la lecture, puis utilise un moteur de synthèse vocale pour le lire.

    Étapes détaillées :
    1. Récupère le texte actuellement dans le presse-papiers à l'aide de la fonction `get_clipboard_text`.
    2. Prépare le texte pour la lecture en effectuant une traduction et en supprimant les lignes indésirables à l'aide de la fonction `prepare_to_read`.
    3. Affiche le texte préparé dans la console, suivi d'un message indiquant que la lecture est en cours.
    4. Initialise un moteur de synthèse vocale (`pyttsx3.Engine`) avec des propriétés spécifiques (vitesse et volume).
    5. Lit le texte préparé à voix haute.
    6. Attend que la lecture soit terminée avant de terminer l'exécution.

    Notes :
    - Le texte est affiché sous forme de représentation (via `__repr__()`) avant d'être lu.
    - La vitesse de lecture est définie à 150 mots par minute, et le volume est réglé à 0.9 (90%).
    """
    text = get_clipboard_text()
    real_text = prepare_to_read(text).__repr__()
    print(real_text + "\nLecture en cours...")
    lecteur = pyttsx3.Engine()
    lecteur.setProperty("rate", 150)
    lecteur.setProperty("volume", 0.9)
    lecteur.say(real_text)
    lecteur.runAndWait()
