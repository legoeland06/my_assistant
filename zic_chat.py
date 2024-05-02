# zic_chat.py
import datetime
import time
import tkinter as tk
from tkinter import PhotoImage, Text, messagebox
import os
import markdown.util
import vosk
import pyaudio
import json
import pyttsx3
import ollama
import markdown
import imageio.v3 as iio
import subprocess
import asyncio

from PIL import Image, ImageTk

# Liste des models déjà téléchargés

WIZARDLM2 = "wizardlm2:latest"
DEEPSEEK_CODER = "deepseek-coder:6.7b"
ALFRED = "alfred:latest"
LLAMA3 = "llama3:latest"
deepseek_coder = "deepseek-coder:latest"
expert = "expert:latest"
gemma = "gemma:latest"
llava = "llava:latest"
mario = "mario:latest"
neural_chat = "neural-chat:latest"
wizard_vicuna_uncensored = "wizard-vicuna-uncensored:30b-q4_0"

# CONSTANTS

WIDTH_TERM = 80
RAPIDITE_VOIX = 150

ROLE_TYPES = [
    "user",
    "assistant",
    "system",
]

ROLE_TYPE = ROLE_TYPES[0]


FICHE_DE_POSTE = "fiche_de_poste"
SCRAP_CONTENT = "content_scrapped"
BROWSE_WITH_BING = "browse"
SCRUM_PROMPT = "prompt_scrum"
CORRECTEUR = "prompt_a_corriger"
SPECIALITY = "speciality"
PROMPTOR = "prompt_to_workd"
DEBATEUR = "subject_to_mind"
FORMATEUR = "sujet_à_traiter"
PRODUCT_OWNER = "projet_à_réaliser"
INVERSE_PROMPT = "inverse_prompt"
CRITIQUE_NOTATIONS = "critique_notations"
EMAIL_WRITER = "e-mail_writer"
TRADUCTEUR = "a_traduire"
EMAIL_WRITER1 = "email_writer1"
BACK_TO_MAIN_MENU = "retour au menu principal"
LANGFR = "Lang=FR-fr, UTF-8"
QUIT_MENU_COMMAND = "/quit"
EXIT_APPLICATION_COMMAND = "/exit"
MODEL_PATH = "vosk-model-fr-0.22"
TRAITEMENT_EN_COURS = "Merci, un instant... Traitement en cours"
TERMINAL_CLEAR = "Terminal effacé"
REPONSE_TROUVEE = "Réponse trouvée..."
FIN_DE_LA_REPONSE = "\nfin de la réponse..."
ASK_TASK = "Faites votre choix"
ASK_FOR_NEW_ROLE = (
    "veuillez préciser le nouveau rôle : assistant, utilisateur ou système ?"
)
URL_ERROR = "erreur d'URL"
QUESTION_URL_WEB_TO_SCROLL = "Veuillez entrer le chemin complet "
WAITING_FOR_INSTRUCTIONS = "Quelles sont vos instructions "
INFOS_PROMPTS = "Exemples de prompts que vous pouvez demander"
NOT_IMPLEMENTED_YET = "... Désolé, mais cette commande n'est pas encore implémentée"
BYEBYE = "d'accord, arrêt de la discussion... Aurevoir Eric, et à bientôt !"
CONVERSATIONS_HISTORY = "voici l'historique des conversations :"
STARS = "*"
LINE = "-"
DOUBLE_LINE = "="
INFOS_CHAT = "\
 ******************************************************\n\
 * COMMANDES ACCESSIBLES du mode chat\n\
 ******************************************************\n\
 * (<f.d.c.p> + ENTRE pour valider.)\n\
 * /quit pour revenir au micro\n\
 * /exit pour fermer l'application\n\
 ******************************************************\n\
 --> "

QUESTIONS = [
    "Fais moi un résumé court de ce texte ci-dessous",
    "Qui sont les auteurs et intervenants ?",
    "Quelles sont les principales idées qui se dégagent",
    "Traduire cette page en Français",
    "combien de mots il y a t-il dans cette page ?",
]

LIENS_APPS = {
    "whatsapp": "",
}
chrome_pid = 0
chrome_pid: subprocess.Popen[str]

GOOGLECHROME_APP = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe "
LIENS_CHROME = {
    "chrome": "",
    "youtube": "https://www.youtube.com/?authuser=0",
    "whatsapp": "https://web.whatsapp.com/",
    "porn": "https://www.xnxx.com/",
    "actualité": "https://news.google.com/home?hl=fr&gl=FR&ceid=FR%3Afr",
    "netflix": "https://www.netflix.com/browse",
    "gmail": "https://mail.google.com/mail/u/0/#inbox",
    "message": "https://messages.google.com/web/conversations/151",
}


PROMPTS_SYSTEMIQUES = {
    SPECIALITY: "Bonjour ! Je souhaite me former à [ speciality ], devenir un top expert sur le sujet. Peux-tu me proposer un programme de formation avec les thématiques à étudier, dans un ordre pertinent ? Tu es un expert en [ speciality ] et aussi un formateur confirmé. Base toi sur tes connaissances en [ speciality ] mais aussi en science de l'éducation pour me proposer le meilleur programme possible. Après ça, je te demanderai de me former sur chacun des points de ton programme",
    INVERSE_PROMPT: "Tu es un expert en Prompt Engineering et en intelligence artificielle générative. J’ai trouvé ce [ inverse_prompt ] que je trouve très bien et je souhaite obtenir un prompt pour générer un [ inverse_prompt ] de ce type.  Peux-tu faire du Reverse Prompt sur ce texte en prenant soin d’identifier le ton et les techniques de rédaction utilisées.",
    EMAIL_WRITER: "En tant que rédacteur d’e-mails expérimenté, je souhaite que tu t’appuies sur ton savoir-faire et des compétences en copywriting. Tu vas m’aider à créer des e-mails clairs et concis, adapté à mon objectif. Tu es capable de comprendre le but et le ton de l’e-mail en fonction de l’objet de l’e-mail et du message de fond.  Avant de rédiger un e-mail, tu dois me permettre de te communiquer les informations clés suivantes : le destinataire, l’objet de l’e-mail, le message et l’objectif de l’e-mail. L’objectif de l’e-mail peut être de toute nature comme un e-mail de prospection, de proposition commerciale, un message de suivi ou encore une newsletter marketing.  Une fois que je t’aurai transmis ces informations clés, tu devras rédiger l’e-mail en le personnalisant avec le nom du destinataire et en prenant soin de dire bonjour et de le conclure efficacement. Pour l’objet, tu me feras une suggestion créative, incitative et accrocheuse.  Dans ton rôle, tu vas prendre soin d’éviter toute erreur de grammaire, d’orthographe et de syntaxe. Ta proposition devra se faire dans un format convivial et prêt à être copiée/collée dans ma boite e-mail. Si c’est OK pour toi, crée une liste à puce avec les infos clés que je dois te transmettre. Je te les communiquerai ensuite et tu pourras rédiger ton e-mail.",
    EMAIL_WRITER1: "En tant que rédacteur d’e-mails expérimenté, je souhaite que tu t’appuies sur ton savoir-faire et des compétences en copywriting. Tu vas m’aider à créer des e-mails clairs et concis, adapté à mon objectif. Tu es capable de comprendre le but et le ton de l’e-mail en fonction de l’objet de l’e-mail et du message de fond.  Avant de rédiger un e-mail, tu dois me permettre de te communiquer les informations clés suivantes : le destinataire, l’objet de l’e-mail, le message et l’objectif de l’e-mail. L’objectif de l’e-mail peut être de toute nature comme un e-mail de prospection, de proposition commerciale, un message de suivi ou encore une newsletter marketing.  Une fois que je t’aurai transmis ces informations clés, tu devras rédiger l’e-mail en le personnalisant avec le nom du destinataire et en prenant soin de dire bonjour et de le conclure efficacement. Pour l’objet, tu me feras une suggestion créative, incitative et accrocheuse.  Dans ton rôle, tu vas prendre soin d’éviter toute erreur de grammaire, d’orthographe et de syntaxe. Ta proposition devra se faire dans un format convivial et prêt à être copiée/collée dans ma boite e-mail.  Voici un email que je veux que tu réécrives dans un style plus formel : [ email_writer1 ]",
    CRITIQUE_NOTATIONS: "Tu es un critique dans divers domaines d’activité, un expert en analyse et en évaluation d’idées, de projets et travaux de toute nature comme la création de contenu, l’entrepreneuriat, l’investissement, la créativité etc.  Tu as toutes les compétences pour bien évaluer la qualité des sujets qu’on te soumet. Tu sais faire des préconisations pertinentes et émettre des feedbacks constructifs, tout en restant bienveillant.  Ta tâche est de noter les idées, projets et travaux que je vais te soumettre en te basant sur les principaux critères d’évaluation dans le domaine concerné.  Selon tes expériences et expertises, tu utiliseras un système de notation de 0 à 5 étoiles pour évaluer la qualité du sujet. À côté de cette note, tu donneras toujours une explication simple et pertinente de ton évaluation en te focalisant sur les principaux critères d’analyse.   À la fin de chaque critique, tu mettras un résumé rapide.  En tant que critique de métier, tu prendras soin d’être toujours objectif et juste dans ton évaluation, en reconnaissant les efforts, la créativité et la prise d’initiative dont je fais preuve pour le sujet que je te soumets.   Réponds « oui » pour valider ces points.  Voici donc mes premiers jets : [ critique_notations ]",
    TRADUCTEUR: "Je veux que tu agisses en tant que traducteur, correcteur, spécialisé en anglais.  Je vais te parler dans n’importe quelle langue. Tu vas détecter la langue et traduire le texte que je te partage en anglais.  Je veux que tu remplaces mes mots et phrases simplifiés de niveau A0 par des mots et des phrases anglais en langage soutenu et élégants d’un point de vue littéraire.  Tu prendras tout de même soin de garder le sens de chaque phrase.  Je souhaite que tu traduises immédiatement le texte, sans aucune explication.  Tu noteras simplement avant la traduction un emoji du drapeau de la langue détectée, une flèche et l’emoji du drapeau du Royaume-Uni.  Voici le texte à traduire sans en modifier le sens : [ a_traduire ] ",
    FORMATEUR: "[Formate ta réponse en utilisant le markdown. Utilise des titres, des sous-titres, des puces et du gras pour organiser tes informations et les rendre plus lisibles. Pour les titres et les sous-titres, prends soin de les rédiger pour qu’ils soient accrocheurs et donnent envie de lire la suite] [ sujet_à_traiter ]",
    DEBATEUR: "Je veux que tu agisses en tant que débatteur professionnel. Tu pourras t’appuyer sur ta culture générale immense et tes compétences en rhétorique. Ta tâche consiste pour chaque sujet que je vais te transmettre à présenter des arguments valables pour chaque côté du débat, réfuter les points de vue opposés dans un tableau contenant 3 colonnes : une pour le chiffre, une avec l’emoji 🔥 pour l’argument et une avec l’emoji ❄️ pour la réfutation. Pour chaque argument et réfutation tu me donneras une phrase explicative complète et a minima une preuve pour la valider. L’objectif est de m’aider à mieux comprendre le sujet en question et à le connaitre plus en profondeur.  C’est pour quoi tu me feras une synthèse objective juste après ton tableau. Mon premier sujet est : [ subject_to_mind ]",
    PRODUCT_OWNER: "Tu es un expert en management de projet. Tu peux t’appuyer sur tes compétences en planification, en conduite du changement et en gestion de la motivation. Pour chaque objectif que je te soumettrai ici, je souhaite que tu me donnes toutes les étapes à suivre pour l’atteindre. Ta réponse doit être formatée dans un tableau en 4 colonnes : une pour la date, une pour l’étape concernée, une pour la description de cette étape et une pour une phrase de motivation relative à l’étape. Utilise les Emojis appropriés pour chaque colonne afin de rendre le tableau agréable à lire et motivant. Réponds uniquement par OK si c’est bon pour toi.",
    SCRUM_PROMPT: """Tu es un expert en gestion de projet, en management et en productivité. Je souhaite être plus efficace et productif dans mon travail. Pour ça, tu vas m’aider à mieux m’organiser et planifier mes tâches.  Pour ça, tu vas t’appuyer sur la méthode SCRUM pour créer une Todo List pertinente et un plan de sprint. La ToDo List devrait inclure toutes les tâches nécessaires pour atteindre l'objectif, et le plan de sprint devrait diviser ces tâches en sprints de deux semaines, avec des objectifs spécifiques pour chaque sprint.  Utilise le Markdown pour mettre en page ta réponse. Mon objectif est le suivant : [ prompt_scrum ]""",
    FICHE_DE_POSTE: """Tu es un expert en recrutement avec une spécialité dans *[METTRE SPÉCIALITÉ DOMAINE]*. Tu maitrises toutes les techniques pour identifier précisément les besoins en recrutement et travailler la fiche de poste optimale. Tu as une approche moderne du recrutement et tes actions sont guidées par les concepts de marque employeur et Employee Advocacy. Je souhaite recruter un *[METTRE POSTE]*. Les missions et caractéristiques du poste sont les suivantes : *[LISTER LES POINTS CLÉS DE L’OFFRE]* Pour rédiger la meilleure fiche de poste possible, tu vas suivre les instructions suivantes : 
Étape 1 : Lister toutes les informations manquantes pour travailler la fiche de poste parfaite et y répondre toi-même en faisant tes meilleures préconisations selon tes compétences et mon contexte. Étape 2 : rédiger un premier jet de la fiche de poste. Étape 3 : faire une critique de cette fiche de poste en lui attribuant une note sur 5 étoiles et en listant les améliorations à lui apporter pour obtenir 5 étoiles sur 5 (la perfection). Étape 4 : améliorer la fiche de poste en fonction de ta critique. 
Point important :
Pour chaque étape, tu attendras ma réponse avant de démarrer la suivante.""",
    SCRAP_CONTENT: """Je suis en train de faire ma veille d’actualité sur [content_scrapped]. Je souhaite que tu m’aides à la réaliser et pour ça, tu vas endosser le rôle d’un expert en curation de contenu. Tu maitrises toutes les techniques pour identifier les meilleures informations, les évaluer et les synthétiser. Voici tes instructions : 
1. Identifie les actualités les plus importantes à retenir aujourd’hui sur [content_scrapped]
2. Présente-les sous forme de tableau avec le titre de l’actualité, la source et un résumé simple des idées clés à retenir
3. Fais une synthèse globale des actus en 100 mots maximum.
4. Convertis cette synthèse dans une vidéo de 60 secondes environ.""",
    BROWSE_WITH_BING: """Tu es un expert en recherche sur Internet et tu maitrises toutes les techniques pour trouver des informations fiables. Tu sais identifier des sources, les évaluer, les recouper et les synthétiser pour les communiquer de manière optimale. Ton rôle est d’aider l’utilisateur à faire une recherche approfondie sur Internet pour [ browse ]. Pour ça, tu vas suivre les étapes suivantes : 
1. Effectue une recherche d’information sur Internet.
2. Présente le lien des sources retenues et fais un résumé pour chacune.
3. Effectue une recherche de sources primaires
4. Présente le lien des sources primaires retenues et fais un résumé pour chacune.
5. Fais une synthèse globale des information et attribue un pourcentage de confiance à ta synthèse.""",
    CORRECTEUR: """[INSTRUCTION]
J’ai un document que je souhaite optimiser pour le web.
Crée un tableau avec 5 à 10 suggestions d’amélioration en mettant dans la colonne de gauche le numéro de la suggestion pour que je puisse les sélectionner. Après le tableau, pose-moi la question « Quelles améliorations souhaites-tu apporter à ton texte ? Choisis-en une ou plusieurs dans le tableau ci-dessus. ». Voici le document : [ prompt_a_corriger ] 
""",
    PROMPTOR: """Tu es un expert en prompt engineering et en intelligence artificielle. Je souhaite que tu sois mon créateur de prompt attitré. Ton nom est « Promptor » et c’est comme ça que je vais t’appeler désormais.
Ton objectif est de me rédiger le meilleur prompt possible selon mes objectifs. Ton prompt doit être rédigé et optimisé pour une requête à ChatGPT (GPT-3.5 ou GPT-4). 
Pour cela, tu vas construire ta réponse de la manière suivante : 
Partie 1 : Le Prompt 
{Fournis-moi le meilleur prompt possible selon ma demande} 
Partie 2 : La critique 
{Réalise une critique sévère du prompt. Pour ça, commence par donner visuellement une note de 0 à 5 étoiles sur 5 pour le prompt (de 0 pour médiocre à 5 pour optimal) et rédige ensuite un paragraphe concis présentant les améliorations à apporter pour que le prompt soit un prompt 5 étoiles. Toutes les hypothèses et/ou problèmes doivent être traités dans ta critique} 
Partie 3 : Les questions 
{Dresse la liste des questions dont la réponse t’est indispensable pour améliorer ton prompt. Pour tout besoin d’information supplémentaire, de contexte ou de précision sur certains points, pose-moi une question. Rédige tes questions sous forme de liste à puce et limite-toi aux questions réellement indispensables} 
Après avoir reçu ta réponse en 3 parties, je vais répondre à tes questions et tu vas répéter ensuite le process en 3 parties. Nous allons continuer à itérer jusqu’à obtenir le prompt parfait. 
Pour ton prompt, tu dois absolument attribuer un ou plusieurs rôles à ChatGPT en fonction de la tâche à réaliser. 
Alors, voici le sujet du prompt que nous allons travailler: [ prompt_to_workd ]""",
}

PREPROMPTS = [
    "Sous forme de listes à puces, donne-moi 10 exemples de questions \n    que je peux te poser, sans donner de détails",
    "Quel est ton nom et que sais-tu faire ?",
    "combien de paramètre possèdes-tu ?",
    "Ecris moi un hello word en Rust et en suite en Java17",
]


def set_pre_prompt(rubrique: str, prompt_name: str):
    return PROMPTS_SYSTEMIQUES[rubrique].replace(rubrique, prompt_name)


def affiche_preprompts():
    print(INFOS_PROMPTS)
    print(STARS * WIDTH_TERM)
    for preprompt in PREPROMPTS:
        print(str(PREPROMPTS.index(preprompt)) + ". " + preprompt)


def engine_lecteur_init():
    lecteur = pyttsx3.init()
    # voice = lecteur.getProperty("voices")[0]  # the french voice
    # lecteur.setProperty(voice, "male")
    lecteur.setProperty("lang", "french")
    lecteur.setProperty("rate", RAPIDITE_VOIX)

    pyttsx3.speak("kiki")
    return lecteur


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


def engine_ecouteur_init():
    # set verbosity of vosk to NO-VERBOSE
    vosk.SetLogLevel(-1)
    # Initialize the model with model-path
    return vosk.Model(MODEL_PATH, lang="fr-fr")


def init_model(model_to_use, prompted: bool = False):
    # model utilisé dans le chatbot
    msg = (
        "Chargement de l'Ia : ["
        + model_to_use[0 : model_to_use.find(":")]
        + "]... Un instant"
    )
    print(msg)
    if not prompted:
        lecteur.say(msg)
        lecteur.runAndWait()
        lecteur.stop()
    return model_to_use


def affiche_menu_pricipale():
    print(
        "\n"
        + STARS * WIDTH_TERM
        + "\nAutres commandes accessibles:\n Dites:"
        + "<Quel jour sommes nous ?> | <lire une page web> | <décrire une image> \n"
        + "<lire un texte> | <est-ce que tu m'écoutes> | <ouvrez chrome> \n"
        + STARS * WIDTH_TERM
        + "\nRemarque : Vous pouvez aussi passer en mode chat"
        + " en disant : < écriture ! > "
    )


def affiche_fille():
    print()
    print(
        '''
                 ,d8888888P:::::d:::::::::::::::::::::::::::::::::::888888888b
                a8888888P:::::::8:::::::::::::::Normand:::::::::::::I888888888
              ,d8888888"::::::::8:::::::::::::::Veilleux::::::::::::I888888888
             ,d8888888P:::::::::8;::::::::::::::::::::::::::::::::::I888888888
            ,d88888888::::::::::Yb;:::::::::::::::::::::::::::::::::I88888888P
           ,d888888888:::::::::::Yb:::::::::::::::::::::::::::::::::I88888888'
           d8888888888;:::::::::::Yb::::::::::::::::::::::::::::::::I8888888'
          ,88888888888b::::::::::::"8;::::::::::::::::::::::::::::::8888888P
          d888888888888b:::::::::::::"Ya;::::::::::;;aa;::::::::::::888888P'
          88888888888888b;:::::::::::::`YbbaaaadddPP"":::::::::::::;88888"
          8888888888888888b;:::a;;;::;ad"8:::::::::::::::::::::::::d88P"
          88888888888888888Y;::::""""":::8:::::::::::::::::::::::::8"
          Y88888888888888888Y;:::::::::::8:::::::::::::::::::::::::8
          `888888888888888888b:::::::::::8:::::::::::::::::::::::::8
           Y888888888888888888:::::::::::8::::::::::::::::::::::::;P
            `"Y888888888888888:::::::::::8::::::::::::::::::::::::d'
               "Y8888P"Y888888:::::::::::8::::::::::::::::::::::::8
                 `"'    `"'  8:::::::::::8::::::::::::::::::::::::8
                             8:::::::::::8::::::::::::::::::::::::8
                             8:::::::::::8;::::::::::::::::::::::;P
                             Y;::::::::::Ib::::::::::::::::::::::d'
                             `b:::::::::::8::::::::::::::::::::::8
                              8:::::::::::8:::::::::::::::::::::;P
                              Y;::::::::::8:::::::::::::::::::::d'
                              `b::::::::::Y;::::::::::::::::::::8
'''
    )
    print()


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


def make_choice(moteur_de_diction, iterable: iter):
    moteur_de_diction(ASK_TASK, True)
    print("\nMENU\n" + STARS * WIDTH_TERM)
    for question in iterable:
        print(str(iterable.index(question)) + ". " + question)
    choix = input(STARS * WIDTH_TERM + "\nVotre choix: ")
    if choix.isnumeric and len(choix) <= 2:
        moteur_de_diction(iterable[int(choix)], True)
        return iterable[int(choix)]
    elif choix.isalpha and len(choix) > 2:
        return choix
    else:
        return QUIT_MENU_COMMAND


def make_choice_dict(moteur_de_diction, dicto: dict):
    moteur_de_diction(ASK_TASK, True)
    print("\nMENU\n" + STARS * WIDTH_TERM)
    inc = 0
    for item in dicto.items():
        item_in_list = list(item)
        if len(item_in_list[1]) > 80:
            print(
                str(inc)
                + ". "
                + item_in_list[0]
                + " :: "
                + item_in_list[1][:80]
                + " ..."
            )
        else:
            print(str(inc) + ". " + item_in_list[0] + " :: " + item_in_list[1])
        inc += 1

    choix_ecrit = input(STARS * WIDTH_TERM + "\nVotre choix_ecrit: ")

    if choix_ecrit.isnumeric and len(choix_ecrit) <= 2:
        choix_reel = list(dicto.items())[int(choix_ecrit)]
        choix_detail = choix_reel[1]
        choix_intitule = choix_reel[0]
        moteur_de_diction(choix_intitule, True)
        return choix_intitule, choix_detail
    elif choix_ecrit.isalpha and len(choix_ecrit) > 2:
        return choix_ecrit, ""
    else:
        return QUIT_MENU_COMMAND, ""


def veullez_patienter(moteur_de_diction):
    moteur_de_diction(TRAITEMENT_EN_COURS, stop_ecoute=True)


def merci_au_revoir(moteur_de_diction, stream_to_stop, pulse_audio_to_stop):
    # Stop and close the stream_to_stop
    moteur_de_diction(BYEBYE, False)
    lecteur.stop()
    stream_to_stop.stop_stream()
    stream_to_stop.close()
    # Terminate the PyAudio object
    pulse_audio_to_stop.terminate()
    exit(0)


def au_revoir():
    exit(0)


def traitement_chat(moteur_de_diction):
    result = mode_chat(moteur_de_diction)
    if result == QUIT_MENU_COMMAND:
        return QUIT_MENU_COMMAND, moteur_de_diction
    if result == "/x":
        result, _ = mode_Super_chat(moteur_de_diction)
    return result, moteur_de_diction


def mode_chat(moteur_de_diction):
    moteur_de_diction("Mode tchat activé", False)
    print("Mode chat activé")
    return input(" ==> ")


def mode_Super_chat(moteur_de_diction):
    moteur_de_diction("Mode multilignes activé", False)
    print("Mode multiligne activé")
    print(INFOS_CHAT)
    buffer = []
    while True:
        try:
            line = input()
            if line == "f.d.c.p":
                return "\n".join(buffer), moteur_de_diction
            elif line == EXIT_APPLICATION_COMMAND:
                au_revoir()
            elif line == QUIT_MENU_COMMAND:
                return "", moteur_de_diction
        except EOFError:
            break
        buffer.append(line)

    multiline_string = "\n".join(buffer)
    return multiline_string, moteur_de_diction


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


def ask_to_ai2(texte, model_to_use, client: ollama.Client):
    ai_response = client.generate(
        model=model_to_use,
        prompt=texte,
        system="",
        template="",
    )
    return ai_response


def ask_to_ai(texte, model_to_use, client: ollama.Client):
    ai_response = client.chat(
        model=model_to_use,
        messages=[
            {
                "role": ROLE_TYPE,
                "content": texte,
            },
        ],
    )
    return ai_response


def traitement_rapide(texte: str, model_to_use, client, talking: bool, moteur_diction):
    ai_response = ask_to_ai(texte, model_to_use=model_to_use, client=client)
    readable_ai_response = ai_response["message"]["content"]

    # kiki:ollama.GenerateResponse=ollama.GenerateResponse()
    # kiki.get('response')

    print(readable_ai_response)
    if talking:
        moteur_diction(readable_ai_response)


def traitement_requete(
    texte: str, file_to_append: str, moteur_diction, model_to_use, client
):
    veullez_patienter(moteur_de_diction=moteur_diction)
    ai_response = ask_to_ai(texte, model_to_use=model_to_use, client=client)
    readable_ai_response = ai_response["message"]["content"]
    append_response_to_file(file_to_append, readable_ai_response)

    moteur_diction(REPONSE_TROUVEE, True)
    print(readable_ai_response)
    return readable_ai_response


class Fenetre_entree:
    content: str
    title: str
    submission: str
    streaming: pyaudio.Stream

    def __init__(self, stream):
        self.title = "ZicChatBot"
        self.content = ""
        self.submission = ""
        self.streaming = stream

    def set(self, content: str):
        self.content = content

    def get(self) -> str:
        return self.content

    def set_submission(self, content: str):
        self.submission = content

    def get_submission(self) -> str:
        return self.submission

    # open a windows
    def creer_fenetre(
        self, msg_to_write, moteur_de_diction, engine_model, title="Lecteur|traducteur"
    ):
        def dicter():
            stream, rec, fenetre_dictee = motors_init()

            def lire_contenu():
                try:
                    kiki = entree_dictee.selection_get()
                    moteur_de_diction(kiki, stop_ecoute=False)
                except:
                    moteur_de_diction(
                        entree_dictee.get("1.0", tk.END), stop_ecoute=False
                    )

            def lance_ecoute() -> str:
                entree_dictee.update()
                while True:
                    reco_text = ""
                    data = stream.read(
                        num_frames=4096, exception_on_overflow=False
                    )  # read in chunks of 4096 bytes
                    if rec.AcceptWaveform(data):  # accept waveform of input voice
                        # Parse the JSON result and get the recognized text
                        result = json.loads(rec.Result())
                        reco_text = result["text"]
                        if "terminer l'enregistrement" in reco_text.lower():
                            moteur_de_diction(
                                "Pause de l'enregistrement. Vous pouvez le reprendre en appuyant sur démarrer la diction.",
                                stop_ecoute=True,
                            )
                            break
                        elif reco_text != "":
                            entree_dictee.insert(tk.END, reco_text + "\n")
                        entree_dictee.update()

            # Création des boutons
            but_frame = tk.Frame(fenetre_dictee)
            but_frame.pack(fill="x", expand=False)

            entree_dictee = tk.Text(fenetre_dictee)
            entree_dictee.configure(bg="white", fg="red")

            entree_dictee.pack(fill="both", expand=True)

            bouton_commencer_diction = tk.Button(
                but_frame, text="commencer la diction", command=lance_ecoute
            )
            bouton_commencer_diction.configure(bg="red", fg="white")

            bouton_commencer_diction.pack(side=tk.LEFT)
            bouton_lire_contenu = tk.Button(
                but_frame, text="lire", command=lire_contenu
            )
            bouton_lire_contenu.pack(side=tk.RIGHT)
            fenetre_dictee.mainloop()

        def motors_init():
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8192,
            )

            my_engine_just_load = engine_model
            rec = vosk.KaldiRecognizer(my_engine_just_load, 16000)

            fenetre_dictee = tk.Tk(
                screenName="Dictée vocale",
                baseName="dictee_vocale",
                className="DicteeVocale",
            )

            return stream, rec, fenetre_dictee

        def soumettre() -> str:
            # Afficher une boîte de message de confirmation
            reponse = messagebox.askyesno(
                "Confirmation", "Êtes-vous sûr de vouloir soumetre ?"
            )
            if reponse:
                self.set_submission(content=entree1.get("1.0", tk.END))
                fenetre.destroy()
            else:
                print("L'utilisateur a annulé.")

        def quitter() -> str:
            # Afficher une boîte de message de confirmation
            reponse = messagebox.askyesno(
                "Confirmation", "Êtes-vous sûr de vouloir quitter ?"
            )
            if reponse:
                self.set_submission(entree1.get("1.0", tk.END))
                fenetre.destroy()
            else:
                print("L'utilisateur a annulé.")

        def lire_texte1():
            moteur_de_diction(entree1.get("1.0", tk.END), True)

        def lire_texte2():
            moteur_de_diction(entree2.get("1.0", tk.END), True)

        def translate_this_text():
            texte_initial = entree1.get("1.0", tk.END)

            # ICI Tester text < 500 caractères
            # sinon le couper en plusieurs texte dans une liste
            def decoupe_texte(texte: str) -> list[list[str]]:

                # on découpe le texte par mots
                liste_of_words = texte.split()
                if len(liste_of_words) >= 500:
                    list_of_large_text: list[list[str]] = []
                    new_list: list[str] = []
                    counter = 0
                    for word in liste_of_words:
                        counter += len(word) + 1
                        new_list.append(word)
                        if counter >= 500:
                            list_of_large_text.append(new_list)
                            new_list = []
                            counter = 0
                    return list_of_large_text
                else:
                    return texte

            if isinstance(decoupe_texte(texte_initial), list):
                for element in decoupe_texte(texte_initial):
                    translated_text = str(translate_it(text_to_translate=element))
                    entree2.insert(tk.END, translated_text)
                    # peut-être ajouter un temporisateur ici
                    # time.sleep(2.5)

            else:
                translated_text = str(
                    translate_it(text_to_translate=decoupe_texte(texte_initial))
                )
                entree2.insert(tk.END, translated_text)
            entree2.update()


            # Création d'un bouton pour Lire
            bouton_lire2.pack(side=tk.RIGHT)
            canvas2.pack(fill="both", expand=True)

        # Création de la fenêtre principale
        fenetre = tk.Tk()
        fenetre.title(self.title + " - " + title)

        # ## PRESENTATION DU GOELAND  ####
        cnvs1 = tk.Frame(fenetre)
        cnvs1.configure(bg=_from_rgb((69, 122, 188)))
        cnvs1.pack(fill="x", expand=False)
        # ################################

        # Create a canvas
        canva = tk.Canvas(cnvs1, height=100, bg=_from_rgb((69, 122, 188)))
        # cnvs = tk.Frame(cnvs1)
        # cnvs.configure(bg=_from_rgb((69, 122, 188)))
        # cnvs.pack(side="right", expand=False)

        label = tk.Label(
            cnvs1,
            text="Jonathan Livingston",
            font=("Trebuchet", 20),
            fg=_from_rgb((240, 240, 240)),
            bg=_from_rgb((69, 122, 188)),
        )

        label.pack(side=tk.RIGHT, expand=False)

        # Load the image file (replace 'test_image.jpg' with your actual image file)
        my_image = ImageTk.PhotoImage(Image.open("IMG_20230619_090300.jpg"))

        # Add the image to the canvas, anchored at the top-left (northwest) corner
        canva.create_image(0, 0, anchor="nw", image=my_image, tags="bg_img")
        canva.pack(fill="x", expand=True)

        # Création des boutons
        button_frame = tk.Frame(fenetre)
        button_frame.pack(fill="x", expand=False)

        canvas1 = tk.Frame(fenetre)
        canvas1.pack(fill="both", expand=True)

        # Création d'un champ de saisie de l'utilisateur
        entree1 = tk.Text(canvas1)
        entree1.configure(bg="grey", fg="white")

        entree1.insert(tk.END, msg_to_write)
        entree1.pack(fill="both", expand=True)

        canvas2 = tk.Frame(fenetre)

        # Création d'un champ de saisie de l'utilisateur
        entree2 = tk.Text(canvas2)
        entree2.configure(bg="green", fg="white")
        entree2.pack(fill="both", expand=True)

        # Création d'un bouton pour Lire
        bouton_lire1 = tk.Button(button_frame, text="Lire", command=lire_texte1)
        bouton_lire1.pack(side=tk.LEFT)
        bouton_lire1.configure(bg="grey", fg="white")

        bouton_lire2 = tk.Button(button_frame, text="Lire", command=lire_texte2)
        bouton_lire2.configure(bg="green", fg="white")

        # Création d'un bouton pour Dicter
        bouton_dicter = tk.Button(button_frame, text="Mode de diction", command=dicter)
        bouton_dicter.configure(bg="red", fg="white")
        bouton_dicter.pack(side=tk.LEFT)

        # Création d'un bouton pour traduction
        bouton_traduire = tk.Button(
            button_frame, text="Traduire", command=translate_this_text
        )
        bouton_traduire.pack(side=tk.LEFT)

        # Création d'un bouton pour soumetre
        bouton_soumetre = tk.Button(button_frame, text="Soumettre", command=soumettre)
        bouton_soumetre.pack(side=tk.LEFT)

        # Création d'un bouton pour quitter
        bouton_quitter = tk.Button(button_frame, text="Quitter", command=quitter)
        bouton_quitter.pack(side=tk.RIGHT)

        # scroll_bar = tkinter.Scrollbar(out_frame3)
        # scroll_bar["bg"] = out_config["bg"]

        # scroll_bar.config(command=out_text.yview)
        # out_text.config(yscrollcommand=scroll_bar.set)

        # Affichage de la fenêtre
        fenetre.mainloop()


def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code"""
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


lecteur = engine_lecteur_init()


def main(prompt=False, stop_talking=False):

    # ##########################################
    # HACK : Détournement de procédure pour bosser
    # test=Fenetre_entree(stream=any)
    # test.creer_fenetre(
    #     engine_model=any,
    #     moteur_de_diction=any,
    #     msg_to_write="TEST"
    # )
    # exit()
    # ##########################################

    client: ollama.Client = ollama.Client(host="http://localhost:11434")

    def inc_lecteur():
        lecteur.setProperty(
            name="rate", value=int(lecteur.getProperty(name="rate")) + 20
        )

    def dec_lecteur():
        lecteur.setProperty(
            name="rate", value=int(lecteur.getProperty(name="rate")) - 20
        )

    def say_tt(alire: str):
        lecteur.say(alire)
        lecteur.runAndWait()
        lecteur.stop()

    def say_txt(alire: str, stop_ecoute: bool):
        if not stop_talking:
            if stop_ecoute:
                arret_ecoute()
            lecteur.say(alire)
            lecteur.runAndWait()
            lecteur.stop()

    if prompt:
        model_used = init_model(LLAMA3, prompted=True)
        return traitement_rapide(
            prompt,
            model_to_use=model_used,
            client=client,
            talking=stop_talking,
            moteur_diction=say_tt,
        )

    model_used = init_model(LLAMA3, prompted=False)

    say_txt("IA initialisée ! ", stop_ecoute=False)

    def text_to_mp3(content: str, lecteur):
        # with open("scenario.txt", "r", encoding="utf-8") as file:
        #     data = file.read().rstrip()
        lecteur.save_to_file(content, "save.mp3")

    def arret_ecoute():
        # print("Arrêt de l'écoute")
        stream.stop_stream()

    def debut_ecoute(info: str = ""):
        say_txt(info, True)
        stream.start_stream()
        return 0, ""

    def write_prompt_to_file(prompt: str):
        output_file.write(
            "::" + datetime.datetime.now().isoformat() + "::" + prompt + "\n"
        )

    def read_prompt_file(file):
        return file.read()

    print(
        "ZicChatbotAudio\n"
        + STARS * WIDTH_TERM
        + "\nChargement... Veuillez patienter\n"
        + STARS * WIDTH_TERM
    )
    model_ecouteur_micro = engine_ecouteur_init()
    say_txt("micro audio initialisé", False)

    # Create a recognizer
    rec = vosk.KaldiRecognizer(model_ecouteur_micro, 16000)
    say_txt("reconnaissance vocale initialisée", False)
    affiche_fille()
    # Open the microphone stream
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=8192,
    )

    # Specify the path for the output text file
    output_file_path = "recognized_text"
    response_file_path = "ai_response"

    resume_file_path = "ai_resume"
    resume_web_page = "ai.resume_web"
    resume_image_page = "ai.resume_image"

    asked_task = ""
    # Open a text file in write mode using a 'with' block
    with open(output_file_path, "a", encoding="utf-8") as output_file:
        # os.system('cls')
        print(
            "\n"
            + STARS * WIDTH_TERM
            + "\nBienvenu dans mon chatbot audio !!! \n"
            + "Dites << TERMINER >> pour finir votre question\n"
            + "Et dites << ARRETER >> pour fermer la discussion\n"
            + STARS * WIDTH_TERM
        )

        affiche_preprompts()
        affiche_menu_pricipale()

        # Start streaming and recognize speech
        time = datetime.datetime.today()

        compteur, recognized_text_before = debut_ecoute(
            "Bonjour Eric. Nous sommes le "
            + time.strftime("%Y-%m-%d")
            + ". Il est exactement "
            + time.strftime("%H:%M:%S")
        )
        while True:
            compteur += 1
            if stream.is_stopped:
                stream.start_stream()

            if compteur % 800 == 0:
                say_txt("Toujours à l'écoute", stop_ecoute=False)

            if compteur % 200 == 0:
                print("!!! Toujours à l'écoute !!!")

            data = stream.read(
                num_frames=4096, exception_on_overflow=False
            )  # read in chunks of 4096 bytes
            if rec.AcceptWaveform(data):  # accept waveform of input voice

                # Parse the JSON result and get the recognized text
                result = json.loads(rec.Result())
                recognized_text = result["text"]

                # IMPORTANT !!!
                # Parce qu'il est positionné en haut de toutes les conditions,
                # la sortie du mode tchat permet de passer aussi des commandes,
                # qui peuvent aussi se faire à la voix
                # exemple : on peut dire < effacer le terminal > ou l'écrire dans le mode tchat
                mode_chat_lance = (
                    "activer le mode d'écriture" in recognized_text.lower()
                    or "activer l'écriture" in recognized_text.lower()
                    or "écriture" == recognized_text.lower()
                    or "passer en mode d'écriture" in recognized_text.lower()
                )
                if mode_chat_lance:
                    multiline_string, _lire_rep = traitement_chat(say_txt)
                    asked_task += "\n" + multiline_string
                    compteur, _ = debut_ecoute()
                    recognized_text = multiline_string

                effaccer_terminal = "effacer le terminal" in recognized_text.lower()

                changer_de_role = (
                    "changer le rôle" == recognized_text.lower()
                    or "changer de rôle" == recognized_text.lower()
                )

                call_preprompts = (
                    "pré prompte" == recognized_text.lower()
                    or "charger des promptes" == recognized_text.lower()
                )

                watch_target_file = (
                    (
                        "lire une page web" in recognized_text.lower()
                        or "lire un texte" in recognized_text.lower()
                    )
                    or ("décrire une image" in recognized_text.lower())
                    or ("charger un fichier texte" in recognized_text.lower())
                    or ("téléchargez un texte" in recognized_text.lower())
                    or ("téléchargez un fichier texte" in recognized_text.lower())
                )

                ne_pas_deranger = "ne pas déranger" in recognized_text.lower()
                activer_parlote = "activer la voix" in recognized_text.lower()
                incremente_lecteur = (
                    "la voie soit plus rapide" in recognized_text.lower()
                )
                decremente_lecteur = (
                    "la voie soit moins rapide" in recognized_text.lower()
                )

                if incremente_lecteur:
                    inc_lecteur()
                    say_txt("voix plus rapide", stop_ecoute=False)
                if decremente_lecteur:
                    dec_lecteur()
                    say_txt("voix plus lente", stop_ecoute=False)

                if ne_pas_deranger:
                    say_txt("ok plus de bruit", stop_ecoute=False)
                    stop_talking = True

                if activer_parlote:
                    stop_talking = False
                    say_txt("ok me re voilà", stop_ecoute=False)

                if effaccer_terminal:
                    os.system("clear")
                    say_txt(TERMINAL_CLEAR, stop_ecoute=True)
                    affiche_menu_pricipale()
                    affiche_preprompts()

                    compteur, recognized_text = debut_ecoute()

                if changer_de_role:
                    print(ASK_FOR_NEW_ROLE)
                    ROLE_TYPE = make_choice(
                        moteur_de_diction=say_txt, iterable=ROLE_TYPES
                    )

                    client.chat(model=model_used, messages=[])
                    compteur, recognized_text = debut_ecoute()

                if call_preprompts:
                    my_dico_prompts = PROMPTS_SYSTEMIQUES
                    the_choice, detail_choice = make_choice_dict(
                        moteur_de_diction=say_txt,
                        dicto=my_dico_prompts,
                    )
                    print("\n" + the_choice + "\n" + STARS * WIDTH_TERM)

                    for elmnt in my_dico_prompts.items():
                        element = elmnt[0]
                        if (
                            the_choice == element
                            and element in my_dico_prompts[element]
                        ):
                            value_prompt_name = traitement_chat(
                                moteur_de_diction=say_txt
                            )[0]
                            break
                        else:
                            value_prompt_name = the_choice

                    instructs = set_pre_prompt(
                        rubrique=element,
                        prompt_name=value_prompt_name,
                    )

                    asked_task = traitement_requete(
                        texte=instructs,
                        file_to_append=response_file_path,
                        moteur_diction=say_txt,
                        model_to_use=model_used,
                        client=client,
                    )
                    actualise_index_html(texte=asked_task, question=instructs)

                    compteur, recognized_text = debut_ecoute()

                if "quel jour sommes-nous" in recognized_text.lower():
                    compteur, recognized_text = debut_ecoute(
                        "Nous sommes le " + time.strftime("%Y-%m-%d")
                    )

                if "quelle heure est-il" in recognized_text.lower():
                    compteur, recognized_text = debut_ecoute(
                        "il est exactement " + time.strftime("%H:%M:%S")
                    )

                if "est-ce que tu m'écoutes" in recognized_text.lower():
                    compteur, recognized_text = debut_ecoute(
                        "oui je suis toujours à l'écoute kiki"
                    )

                if (
                    "effacer l'historique" in recognized_text.lower()
                    or "supprimer l'historique" in recognized_text.lower()
                ):
                    asked_task = ""
                    say_txt("historique effacé", stop_ecoute=False)
                    compteur, recognized_text = debut_ecoute("je vous écoute")

                if (
                    "afficher l'historique des questions" in recognized_text.lower()
                    or "affiche l'historique des questions" in recognized_text.lower()
                ):

                    if len(asked_task) > 500:
                        print(
                            "\nvoici l'historique :\n"
                            + STARS * WIDTH_TERM
                            + "\n... "
                            + asked_task[490:]
                        )
                    else:
                        print(
                            "\nvoici l'historique :\n"
                            + STARS * WIDTH_TERM
                            + "\n "
                            + asked_task
                        )

                    say_txt("Voici l'historique", stop_ecoute=False)
                    compteur, recognized_text = debut_ecoute("je vous écoute")

                if (
                    "afficher l'historique des conversations" in recognized_text.lower()
                    or "affiche l'historique des conversations"
                    in recognized_text.lower()
                ):
                    say_txt("d'accord...", stop_ecoute=True)
                    with open(
                        resume_web_page + ".html", "r", encoding="utf-8"
                    ) as file_to_read:
                        conversation_hystory = file_to_read.read()

                    result = (
                        CONVERSATIONS_HISTORY
                        + "\n"
                        + STARS * WIDTH_TERM
                        + "\n"
                        + conversation_hystory
                    )
                    # Appel de la fonction pour créer la fenêtre
                    say_txt(CONVERSATIONS_HISTORY, stop_ecoute=False)
                    call_editor_talker(
                        say_txt=say_txt,
                        streaming=stream,
                        engine=model_ecouteur_micro,
                        text_init=result,
                    )

                    compteur, recognized_text = debut_ecoute("je vous écoute")

                # ici appel générique OUVRIR ou OUVREZ + MOTCLE
                for lien in LIENS_CHROME:
                    links_chrome = (
                        ("ouvrir " + lien in recognized_text.lower())
                        or (
                            recognized_text.lower() in lien
                            and "ouvrir" in recognized_text_before
                        )
                        or ("ouvrez " + lien in recognized_text.lower())
                        or (
                            recognized_text.lower() in lien
                            and "ouvrez" in recognized_text_before
                        )
                    )
                    if links_chrome:
                        say_txt("ouverture de " + lien, stop_ecoute=False)
                        chrome_pid = lancer_chrome(url=LIENS_CHROME[lien]).pid
                        compteur, recognized_text = debut_ecoute(
                            lien + " à été lancé..."
                        )
                        recognized_text_before = recognized_text
                        break

                if (
                    "lire à haute voix" in recognized_text.lower()
                    or "editeur" == recognized_text.lower()
                ):
                    asked_task = call_editor_talker(
                        say_txt, streaming=stream, engine=model_ecouteur_micro
                    )

                    actualise_index_html(
                        texte=traitement_requete(
                            texte=asked_task,
                            client=client,
                            moteur_diction=say_txt,
                            model_to_use=model_used,
                            file_to_append=resume_web_page,
                        ),
                        question=asked_task,
                    )

                    compteur, _ = debut_ecoute("je vous écoute")

                if "sauvegarder vers un fichier audio" in recognized_text.lower():
                    # multiline_string, _lire_rep = mode_Super_chat(say_txt)
                    text_to_mp3(
                        call_editor_talker(
                            say_txt, streaming=stream, engine=model_ecouteur_micro
                        ),
                        lecteur=lecteur,
                    )
                    compteur, recognized_text = debut_ecoute("sauvegarde effectuée")

                if "fermer chrome" in recognized_text:
                    say_txt("fermer chrome " + NOT_IMPLEMENTED_YET, stop_ecoute=False)
                    compteur, recognized_text = debut_ecoute()
                    recognized_text_before = recognized_text

                if "télécharger mes e-mails" in recognized_text:
                    say_txt(
                        "télécharger mes e-mails " + NOT_IMPLEMENTED_YET,
                        stop_ecoute=False,
                    )
                    compteur, recognized_text = debut_ecoute()
                    recognized_text_before = recognized_text

                if watch_target_file:
                    link_url: str = ""

                    def enter_url() -> str:
                        print(
                            "\n"
                            + QUESTION_URL_WEB_TO_SCROLL
                            + "\n"
                            + STARS * WIDTH_TERM
                        )
                        say_txt(QUESTION_URL_WEB_TO_SCROLL, True)
                        my_url = input("url: ")
                        if my_url == "":
                            say_txt(URL_ERROR, True)
                            return enter_url()
                        elif QUIT_MENU_COMMAND == my_url:
                            return QUIT_MENU_COMMAND
                        else:
                            return lire_url(my_url)

                    link_url = enter_url()
                    while link_url == "":
                        link_url = enter_url()

                    instruction: str = ""
                    if QUIT_MENU_COMMAND != link_url:
                        say_txt(WAITING_FOR_INSTRUCTIONS, False)
                        instruction = make_choice(
                            moteur_de_diction=say_txt, iterable=QUESTIONS
                        )

                        if instruction != QUIT_MENU_COMMAND:
                            url_content = link_url
                            asked_task = "\n" + instruction + "\n" + url_content
                            actualise_index_html(
                                texte=traitement_requete(
                                    asked_task,
                                    resume_web_page,
                                    moteur_diction=say_txt,
                                    model_to_use=model_used,
                                    client=client,
                                ),
                                question=asked_task,
                            )
                            compteur = debut_ecoute()
                        else:
                            compteur, recognized_text = debut_ecoute(BACK_TO_MAIN_MENU)

                    else:
                        compteur, recognized_text = debut_ecoute(BACK_TO_MAIN_MENU)

                    compteur, recognized_text = debut_ecoute(BACK_TO_MAIN_MENU)

                # TODO : AJOUTER UN PREPROMPT DE SYSTEM POUR AFFINER

                # Check for the termination keyword
                if "terminé" == recognized_text.lower() and asked_task != "":
                    print(
                        "---------------------------------------------\nOk. Traitement..."
                    )
                    print("Question en traitement, un instant...")

                    actualise_index_html(
                        texte=traitement_requete(
                            client=client,
                            moteur_diction=say_txt,
                            model_to_use=model_used,
                            file_to_append=response_file_path,
                            texte=asked_task,
                        ),
                        question=asked_task,
                    )

                    # asked_task=""
                    compteur, recognized_text = debut_ecoute("je vous écoute")

                # Write recognized text to the file
                if recognized_text != "":
                    print("Prompt::" + recognized_text)
                    recognized_text_before = recognized_text
                    write_prompt_to_file(recognized_text)
                    asked_task += "\n" + recognized_text + "\n"

                if (
                    "arrêtez" in recognized_text.lower()
                    or "stoppez" in recognized_text.lower()
                ):
                    asked_task = ""
                    recognized_text = ""
                    merci_au_revoir(
                        say_txt, stream_to_stop=stream, pulse_audio_to_stop=p
                    )


def call_editor_talker(say_txt, streaming, engine, text_init="") -> str:
    say_txt("D'accord !", stop_ecoute=True)
    fenetre_de_lecture = Fenetre_entree(stream=streaming)
    if text_init != "":
        msg = text_init
    else:
        msg = "Coller ici le texte à lire à haute voix, puis cliquez sur <lire>"
    fenetre_de_lecture.creer_fenetre(
        msg_to_write=msg, moteur_de_diction=say_txt, engine_model=engine
    )
    if input("Voulez-vous soummetre votre texte à l'IA (o/n)?") == "o":
        texte_lu = fenetre_de_lecture.get_submission()
        if len(texte_lu) > 500:
            print(texte_lu[:499] + "... ")
        else:
            print(texte_lu)
        say_txt("requette soumise à l'IA... Veuillez patienter", stop_ecoute=True)

    return fenetre_de_lecture.get_submission()


def run_start_translating(text_to_translate):
    loop = asyncio.get_event_loop()
    rs = loop.run_until_complete(
        async_translate_it(text_to_translate=text_to_translate)
    )
    return rs


async def async_translate_it(text_to_translate: str):
    return await translate_it(text_to_translate=text_to_translate)


def translate_it(text_to_translate: str) -> str:
    """
    traduit le text reçu par maximum de 500 caractères. Si le text est une liste, on la traduit une à une str
    @param text: desired text to translate, maximum de 500 caractères
    @return: str: translated text
    """

    # Use any translator you like, in this example GoogleTranslator
    from deep_translator import GoogleTranslator as zic_translator

    if not isinstance(text_to_translate,str):
        reformat_translated=" ".join(str(x) for x in text_to_translate)
    else :
        reformat_translated=text_to_translate

    translated = zic_translator(source="auto", target="fr").translate(
        text=reformat_translated
    )  # output -> Weiter so, du bist großartig

    print(translated)
    return translated


def actualise_index_html(texte: str, question: str):
    if len(question) > 500:
        question = question[:499] + "..."
    with open("index" + ".html", "a", encoding="utf-8") as file_to_update:
        markdown_response = markdown.markdown(texte, output_format="xhtml")
        markdown_question = markdown.markdown(question, output_format="xhtml")
        file_to_update.write(
            "<div id='response_ai'>"
            + "<div id=question_to_ai>"
            + "<h3>Prompt</h3>"
            + markdown_question
            + "\n"
            + "</div>"
            + markdown_response
            + "\n"
            + "</div>"
        )


def return_result(say_txt, result_):
    print(result_)
    say_txt(result_, stop_ecoute=False)
    recognized_text = ""
    return recognized_text


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create a ArcHydro schema")
    parser.add_argument(
        "--prompt", metavar="prompt", required=False, help="the prompt to ask"
    )
    parser.add_argument(
        "--talk", metavar="talk", required=False, help="set talking to on"
    )
    args = parser.parse_args()

    main(prompt=args.prompt, stop_talking=args.talk)
