# zic_chat.py
import datetime
import vosk
import pyaudio
import json
import pyttsx3
import ollama
import os,signal
import markdown
import imageio.v3 as iio
import subprocess

# Liste des models déjà téléchargés
WIZARDLM2="wizardlm2"
DEEPSEEK_CODER="deepseek-coder:6.7b"
ALFRED="Alfred:latest"
LLAMA3="llama3:latest"

# CONSTANTS

WIDTH_TERM=40

ROLE_TYPES=[
    "user",
    "assistant",
    "system",
]

ROLE_TYPE=ROLE_TYPES[0]

LANGFR=" En français "
QUIT_MENU_COMMAND="/quit"
EXIT_APPLICATION_COMMAND="/exit"
MODEL_PATH = "vosk-model-fr-0.22"
TRAITEMENT_EN_COURS="Merci, un instant... Traitement en cours"
REPONSE_TROUVEE = "Réponse trouvée..."
FIN_DE_LA_REPONSE = "\nfin de la réponse..."
ASK_TASK="Faites votre choix"
INFOS_PROMPTS="Exemples de prompts que vous pouvez demander"
BYEBYE="d'accord, arrêt de la discussion... Aurevoir Eric, et à bientôt !"
STARS="*"
LINE="-"
DOUBLE_LINE="="
INFOS_CHAT="""
******************************************************
COMMANDES ACCESSIBLES du mode chat
******************************************************
(<f.d.c.p> + ENTRE pour valider.)
/quit pour revenir au micro
/exit pour fermer l'application
******************************************************
 --> """

QUESTIONS=[
        "Fais moi un résumé court de ce texte ci-dessous",
        "Qui sont les auteurs et intervenants ?",
        "Quelles sont les principales idées qui se dégagent",
        "Traduire cette page en Français",
        "combien de mots il y a t-il dans cette page ?",
        ]

LIENS_APPS={
    'whatsapp':""
}

GOOGLECHROME_APP="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe "
LIENS_CHROME={
    'chrome':'',
    'youtube':'https://www.youtube.com/?authuser=0',
    'actualité':'https://news.google.com/home?hl=fr&gl=FR&ceid=FR%3Afr',
    'netflix':'https://www.netflix.com/browse',
    'gmail':'https://mail.google.com/mail/u/0/#inbox',
    'message':'https://messages.google.com/web/conversations/151'
}


PREPROMPTS=[
    "Sous forme de listes à puces, donne-moi 10 exemples de questions que je peux te poser, sans donner de détails",
    "Quel est ton nom et que sais-tu faire ?",
    "combien de paramètre possèdes-tu ?",
    "Ecris moi un hello word en Rust et en suite en Java17"
]


def affiche_preprompts():
    print(INFOS_PROMPTS)
    print(STARS)
    for preprompt in PREPROMPTS:
        print(str(PREPROMPTS.index(preprompt))+". "+preprompt)

def engin_init():
    engine = pyttsx3.init()
    voice = engine.getProperty('voices')[0] # the french voice
    engine.setProperty(voice, 'male')
    engine.setProperty('lang', 'french')
    engine.setProperty('rate',200)
    return engine

def lancer_chrome(url:str)->subprocess.Popen[str]:
    return subprocess.Popen(GOOGLECHROME_APP+url,text=True,shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)


def tester_appellation(appelation:str)->str:
    for lien in LIENS_CHROME:
        if lien in appelation:
            chrome_pid=lancer_chrome(url=LIENS_CHROME[lien])
            return lien

def init_engin():
    # set verbosity of vosk to NO-VERBOSE
    vosk.SetLogLevel(-1)
    # Initialize the model with model-path
    return vosk.Model(MODEL_PATH,lang="fr-fr")

def init_model(model_to_use):
    # model utilisé dans le chatbot
    msg="Chargement de l'Ia : ["+model_to_use[0:model_to_use.find(':')]+"]... Un instant"
    print(msg)
    engine.say(msg)
    engine.runAndWait()
    engine.stop()
    return model_to_use

def affiche_menu_pricipale():
    print(STARS*WIDTH_TERM+"\nAutres commandes accessibles:\n Dites:\
 <Quel jour sommes nous ?> | <lire une page web> | <fichiers images> | <étude web> | <fichier texte> | <est-ce que tu m'écoute> | <lancez chrome> \n\
          Vous pouvez aussi m'écrire en me disant : <passe en mode écriture> ")
    
def lire_fichier(file_name:str)->str:
    
    with open(file_name+'.txt', 'r',encoding='utf-8') as file:
        if file.readable():
            data_file = file.read().rstrip()
            return "fais moi un résumé de ce texte: "+data_file
        else : 
            return ""

def lire_url(url:str)->str:
    return url

def lire_image(name:str)->any:
    
    # Load a single image
    im = iio.imread(name)
    print(im.shape)  # Shape of the image (height, width, channels)
    return im

def make_choice(moteur_de_diction,iterable:iter):
    moteur_de_diction(ASK_TASK,True)
    print("\nMENU\n"+STARS*WIDTH_TERM)
    for question in iterable:
        print(str(iterable.index(question))+". "+question)
    choix=input(STARS*WIDTH_TERM+"\nVotre choix: ")
    if choix.isnumeric and len(choix)==1:
        moteur_de_diction(iterable[int(choix)],True)
        return iterable[int(choix)]
    else :
        return "quit"
    
def veullez_patienter(moteur_de_diction):
    moteur_de_diction(TRAITEMENT_EN_COURS,stop_ecoute=True)

def merci_au_revoir(moteur_de_diction,stream_to_stop,pulse_audio_to_stop):
    # Stop and close the stream_to_stop
    moteur_de_diction(BYEBYE,False)
    engine.stop()
    stream_to_stop.stop_stream()
    stream_to_stop.close()
    # Terminate the PyAudio object
    pulse_audio_to_stop.terminate()
    exit(0)

def au_revoir():
    exit(0)

def mode_chat(moteur_de_diction):
    moteur_de_diction("Mode tchat activé",False)
    print(INFOS_CHAT)
    buffer = []
    while True:
        try:
            line = input()
            if line == "f.d.c.p":
                break
            elif line == EXIT_APPLICATION_COMMAND:
                au_revoir()
            elif line == QUIT_MENU_COMMAND:
                return "",moteur_de_diction
        except EOFError:
            break
        buffer.append(line)

    multiline_string = "\n".join(buffer)
    return multiline_string,moteur_de_diction

def append_response_to_file(file_to_append, readable_ai_response):
        with open(file_to_append, "a",encoding="utf-8") as target_file:
            markdown_content = markdown.markdown(readable_ai_response,output_format="xhtml")
            
            target_file.write('::'+datetime.datetime.now().isoformat()+"::\n"+markdown_content+"\n")

def ask_to_ai(texte,model_to_use):
    ai_response = client.chat(model=model_to_use,messages=[{'role': ROLE_TYPE,'content':texte,},])
    return ai_response
    # jusqu'ici je pense

def traitement_requete(texte:str,file_to_append:str,moteur_diction,model_to_use):
    veullez_patienter(moteur_de_diction=moteur_diction)
    ai_response = ask_to_ai(texte,model_to_use=model_to_use)
    readable_ai_response=ai_response["message"]["content"]
    append_response_to_file(file_to_append, readable_ai_response)  

    print(readable_ai_response)

    moteur_diction(REPONSE_TROUVEE+readable_ai_response+FIN_DE_LA_REPONSE,True)


chrome_pid:subprocess.Popen[str]
engine = engin_init()
client = ollama.Client(host='http://localhost:11434')

def main():

    def say_txt(alire :str,stop_ecoute:bool) :
        if stop_ecoute : arret_ecoute()
        engine.say(alire)
        engine.runAndWait()
        engine.stop()
        
    def text_to_mp3() :
        with open('scenario.txt', 'r',encoding='utf-8') as file:
            data = file.read().rstrip()
        engine.save_to_file(data , 'scenario.mp3')

    def arret_ecoute():
        # print("Arrêt de l'écoute")
        stream.stop_stream()
        
    def debut_ecoute():
        print("Je vous écoute !")
        say_txt("Je vous écoute",True)
        stream.start_stream()

    def write_prompt_to_file(prompt:str):
        output_file.write('::'+datetime.datetime.now().isoformat()+"::\n"+ prompt + "\n")


    print("Chargement...")
    model_voix=init_engin()
    say_txt("moteur audio initialisé",False)
    model_used=init_model(LLAMA3)
    print("modele initialisé")
    
    # Create a recognizer
    rec = vosk.KaldiRecognizer(model_voix, 16000)
    say_txt("reconnaissance vocale initialisée",False)

    # Open the microphone stream
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=8192)

    # Specify the path for the output text file
    output_file_path = "recognized_text.html"
    response_file_path = "ai_response.html"
    resume_file_path= "ai_resume.html"
    resume_web_page="ai.resume_web.html"
    resume_image_page="ai.resume_image.html"



    # Open a text file in write mode using a 'with' block
    with open(output_file_path, "a",encoding="utf-8") as output_file:
        # os.system('cls')
        print("\n"+STARS*WIDTH_TERM+"\nBienvenu dans mon chatbot audio !!! \n\
              Dites << TERMINER >> pour finir votre question\n\
              Et dites << ARRETER >> pour fermer la discussion\n"+STARS*WIDTH_TERM)
        affiche_preprompts()
        affiche_menu_pricipale()
        say_txt("Bonjour éric",True)
        
        debut_ecoute()
        asked_task=""
        # Start streaming and recognize speech
        time=datetime.datetime.today()

        recognized_text_before=""
        while True:
            data = stream.read(num_frames=4096,exception_on_overflow=False)#read in chunks of 4096 bytes
            if rec.AcceptWaveform(data):#accept waveform of input voice

                # Parse the JSON result and get the recognized text
                result = json.loads(rec.Result())
                recognized_text = result['text']

                if "change le rôle" == recognized_text.lower() or "change de rôle" == recognized_text.lower():
                    print("veuillez préciser le nouveau rôle : assistant, utilisateur ou système ?")
                    say_txt("veuillez préciser le nouveau rôle : assistant, utilisateur ou système ?",stop_ecoute=True)
                    ROLE_TYPE=make_choice(moteur_de_diction=say_txt,iterable=ROLE_TYPES)
                    recognized_text=""
                    debut_ecoute()
                    

                if "l'écriture"==recognized_text.lower() or "écriture"==recognized_text.lower() or "mode d'écriture"==recognized_text.lower():
                    multiline_string,_lire_rep = mode_chat(moteur_de_diction=say_txt)
                    if multiline_string!="":
                        # multiline_string = mode_chat(say_txt=say_txt)[0]
                        asked_task+="\n"+LANGFR+"\n"+multiline_string+LANGFR
                        traitement_requete(texte=asked_task,file_to_append=resume_web_page,moteur_diction=_lire_rep,model_to_use=model_used)
                        # on réouvre le micro
                    debut_ecoute()
                    
                if "quel jour sommes-nous" in recognized_text.lower():
                    say_txt("Nous sommes le "+time.strftime("%Y-%m-%d"),stop_ecoute=False)
                    recognized_text=""
                if "quelle heure est-il" in recognized_text.lower():
                    say_txt("il est exactement "+time.strftime("%H:%M:%S"),stop_ecoute=False)
                    recognized_text=""
                if ("est-ce que tu m'écoute" in recognized_text.lower()):
                    say_txt("oui je suis toujours à l'écoute kiki",stop_ecoute=False)
                    recognized_text=""

                if "efface l'historique" in recognized_text.lower():
                    asked_task=""
                    say_txt("historique effacé",stop_ecoute=False)
                    recognized_text=""

                # ici appel générique OUVRIR + MOTCLE
                # test direct des liens
                for lien in LIENS_CHROME:
                    if ("ouvrir "+lien in recognized_text.lower()) or (recognized_text.lower() in lien and "ouvrir" in recognized_text_before) :
                        lancer_chrome(url=LIENS_CHROME[lien])
                        # return lien
                        say_txt("ouverture de "+lien,stop_ecoute=False)
                        say_txt(lien+" à été lancé...",stop_ecoute=False)
                        recognized_text=recognized_text_before=""
                        break


                if "fermer chrome" in recognized_text:
                    # signal.Signals.SIGTERM
                    say_txt("fermer chrome... Désolé, mais cette commande n'est pas encore implémentée",stop_ecoute=False)
                    recognized_text=recognized_text_before=""

                if ("lire une page web" in recognized_text.lower()):
                    contenu_web:str=""
                    def enter_url()->str:
                        print("""
url complet de la page web étudier 
***********************************""")
                        say_txt("Veuillez entrer l'url complet de la page web à étudier",True)
                        my_url=input("url: ")
                        if my_url=="" :
                            say_txt("erreur d'URL",True)
                            enter_url()
                        elif QUIT_MENU_COMMAND==my_url :
                            return "quitthismenu"
                        else : 
                            return lire_url(my_url)
                    
                    
                    while len(contenu_web.__str__())<10 or "quitthismenu"==contenu_web:
                        if "quitthismenu"==contenu_web: 
                            recognized_text=""
                            debut_ecoute()
                            break
                        contenu_web=enter_url()
                        
                    instruction:str=""
                    if not "quitthismenu"==contenu_web:
                        say_txt("Page web en attente de lecture...",False)
                        instruction = make_choice(moteur_de_diction=say_txt,iterable=QUESTIONS)
                        
                        if instruction==QUIT_MENU_COMMAND :
                            recognized_text=""
                            debut_ecoute()
                            continue
                        
                        asked_task+="\n"+instruction+"\n"+contenu_web
                        traitement_requete(asked_task,resume_web_page,moteur_diction=say_txt,model_to_use=model_used)
                        
                    debut_ecoute()
                    
                if "qu'est-ce qu'il y a dans cette image" in recognized_text.lower():
                    my_file_name:str=""
                    contenu_du_fichier:str=""
                    def enter_name_file(contenu):
                        print("""
Chemin complet du fichier à étudier 
***********************************                             
""")
                        say_txt("Veuillez entrer le chemin complet du fichier à étudier",True)
                        my_file_name=input(": ")
                        if my_file_name=="" :
                            say_txt("erreur de nom de fichier",True)
                            enter_name_file(contenu)
                        elif QUIT_MENU_COMMAND==my_file_name :
                            return "quitthismenu"
                        else : 
                            contenu+="\n"+"qu'est-ce qu'il y a dans cette image ? "+my_file_name
                            contenu+="\n"+LANGFR+"\n"+asked_task
                            traitement_requete(contenu,resume_web_page,say_txt,model_used)

                            debut_ecoute()
                    
                    while len(contenu_du_fichier.__str__())<10 or "quitthismenu"==contenu_du_fichier:
                        if "quitthismenu"==contenu_du_fichier: 
                            recognized_text=""
                            debut_ecoute()
                            break
                        contenu_du_fichier=enter_name_file(contenu=asked_task)
                        
                    instruction:str=""
                    
                if  ("charger un texte" in recognized_text.lower()) or ("charger un fichier texte" in recognized_text.lower()) \
                    or ("téléchargez un texte" in recognized_text.lower()) or ("téléchargez un fichier texte" in recognized_text.lower()) :
                    my_file_name:str=""
                    contenu_du_fichier:str=""
                    def enter_name_file()->str:
                        print("""
Chemin complet du fichier à étudier 
***********************************                             
""")
                        say_txt("Veuillez entrer le chemin complet du fichier à étudier",True)
                        my_file_name=input(": ")
                        if my_file_name=="" :
                            say_txt("erreur de nom de fichier",True)
                            enter_name_file()
                        elif QUIT_MENU_COMMAND==my_file_name :
                            return "quitthismenu"
                        else : 
                            return lire_fichier(my_file_name)
                    
                    
                    while len(contenu_du_fichier.__str__())<10 or "quitthismenu"==contenu_du_fichier:
                        if "quitthismenu"==contenu_du_fichier: 
                            recognized_text=""
                            debut_ecoute()
                            break
                        contenu_du_fichier=enter_name_file()
                        
                    instruction:str=""
                    if not "quitthismenu"==contenu_du_fichier:
                        say_txt("Document en attente de lecture...",False)
                        instruction = make_choice(moteur_de_diction=say_txt,iterable=QUESTIONS)
                        
                        if instruction==QUIT_MENU_COMMAND : 
                            recognized_text=""
                            debut_ecoute()
                            continue
                        
                        asked_task+="\n"+LANGFR+"\n"+instruction+"\n"+contenu_du_fichier+LANGFR
                        traitement_requete(asked_task,response_file_path,say_txt,model_used)
                        
                        debut_ecoute()

                # TODO : AJOUTER UN PREPROMPT DE SYSTEM POUR AFFINER
                
                # Check for the termination keyword
                if "terminé" in recognized_text.lower() and asked_task!="":
                    print("---------------------------------------------\nOk. Traitement...")

                    # On pose la question à lAi Ollama
                    print("Question à l'Ia::"+asked_task)
                    print("Question en traitement, un instant...")
                    asked_task=LANGFR+"\n"+asked_task
                    traitement_requete(asked_task,response_file_path,say_txt,model_used)

                    asked_task=""
                    recognized_text=""
                    debut_ecoute()
                
                # Write recognized text to the file
                if recognized_text!="":
                    print("Prompt::"+recognized_text)
                    recognized_text_before=recognized_text
                    write_prompt_to_file(recognized_text)
                    asked_task+=recognized_text+"\n"

                if "arrêtez" in recognized_text.lower():
                    asked_task=""
                    recognized_text=""
                    merci_au_revoir(say_txt,stream_to_stop=stream,pulse_audio_to_stop=p)

if __name__ == '__main__':
    main()