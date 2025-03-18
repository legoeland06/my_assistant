# Projet de Traduction et Lecture de Texte

## Description

Ce projet permet de récupérer du texte depuis le presse-papiers, de le traduire en français en utilisant l'API Google GenAI, de nettoyer le texte traduit en supprimant certains caractères et lignes indésirables, puis de lire le texte nettoyé à haute voix.

## Fonctionnalités

- Récupération du texte depuis le presse-papiers.
- Traduction du texte en français en utilisant l'API Google GenAI.
- Nettoyage du texte traduit en supprimant certains caractères et lignes indésirables.
- Lecture du texte nettoyé à haute voix.

## Modules Utilisés

- `pyperclip`: Module Python multiplateforme pour les opérations sur le presse-papiers.
- `pyttsx3`: Bibliothèque de conversion texte-parole en Python.
- `google.genai`: Module pour interagir avec l'API Google GenAI.
- `secret`: Module pour stocker les clés secrètes.
- `pydantic`: Bibliothèque de validation des données et de gestion des paramètres.

## Classes

- `Recipe(BaseModel)`: Modèle Pydantic pour la réponse de l'API.

## Fonctions

- `get_clipboard_text()`: Récupère le texte actuel du presse-papiers.
- `translate_it(text_to_translate: str | list, initial: str = "français", target: str = "français") -> str`: Traduit le texte donné de la langue initiale à la langue cible en utilisant l'API Google GenAI.
- `prepare_to_read(text: str) -> list`: Prépare le texte donné pour la lecture en le traduisant en français et en supprimant certains caractères et lignes indésirables.

## Utilisation

Exécutez le script pour récupérer le texte du presse-papiers, le traduire, le nettoyer et le lire à haute voix.

## Exemple d'Exécution

```python
if __name__ == "__main__":
    text = get_clipboard_text()
    real_text = prepare_to_read(text).__repr__()
    print(real_text + "\nLecture en cours...")
    lecteur = pyttsx3.Engine()
    lecteur.setProperty("rate", 150)
    lecteur.setProperty("volume", 0.9)
    lecteur.say(real_text)
    lecteur.runAndWait()
```

## Configuration

Assurez-vous d'avoir les modules nécessaires installés et configurez les clés API dans le module `secret`.

## Auteurs

- Eric Bruneau