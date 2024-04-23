# zic_chat.py

import vosk
import pyaudio
import json
import pyttsx3
import ollama
import os
 
QUESTIONS=[
    "Fais moi un résumé court de ce texte ci-dessous",
    "Qui sont les auteurs et intervenants ?",
    "Quelles sont les principales idées qui se dégagent",
    "Traduire cette page en Français",
    "combien de mots il y a t-il dans cette page ?",
]

def lire_fichier(file_name:str)->str:
    
    with open(file_name+'.txt', 'r',encoding='utf-8') as file:
        if file.readable():
            data_file = file.read().rstrip()
            return "fais moi un résumé de ce texte: "+data_file
        else : 
            return ""

def lire_url(url:str)->str:
    return url

def make_choice(lire_reponse):
    lire_reponse("Quelle tâche voulez vous accomplir ?",False)
    print("\nMENU\n*****************************************")
    for question in QUESTIONS:
        print(str(QUESTIONS.index(question))+". "+question)
    choix=input("*****************************************\nVotre choix: ")
    if choix.isnumeric and len(choix)==1:
        return QUESTIONS[int(choix)]
    else :
        return "quit"

def main():
    MODEL="wizardlm2"

    engine = pyttsx3.init()
    voice = engine.getProperty('voices')[0] # the french voice
    engine.setProperty(voice, 'french')
    engine.setProperty('rate',200)
    
    client = ollama.Client(host='http://localhost:11434')
    ollama.show(MODEL)
    client_to_web = ollama.Client()

    # Set the model path
    model_path = "vosk-model-fr-0.22"
    # Initialize the model with model-path
    model = vosk.Model(model_path,lang="fr-fr")

    # Create a recognizer
    rec = vosk.KaldiRecognizer(model, 16000)

    # Open the microphone stream
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=8192)

    # Specify the path for the output text file
    output_file_path = "recognized_text.txt"
    response_file_path = "ai_response.md"
    resume_file_path= "ai_resume.md"
    resume_web_page="ai.resume_web.md"
    
    def lire_reponse(alire :str,validation:bool) :
        if validation : arret_ecoute()
        engine.say(alire)
        engine.runAndWait()
        engine.stop()
        
    def text_to_audio() :
        with open('scenario.txt', 'r',encoding='utf-8') as file:
            data = file.read().rstrip()
        engine.save_to_file(data , 'scenario.mp3')

    def arret_ecoute():
        # print("Arrêt de l'écoute")
        stream.stop_stream()
        
    def debut_ecoute():
        print("Je vous écoute !")
        lire_reponse("Je vous écoute",True)
        stream.start_stream()

    # Open a text file in write mode using a 'with' block
    with open(output_file_path, "w",encoding="utf-8") as output_file:
        os.system('cls')
        print("\n****************************************************\nBienvenu dans mon chatbot audio !!! \nDites << TERMINER >> pour finir votre question\nEt dites << ARRETER >> pour fermer la discussion\n****************************************************")
        lire_reponse("Bonjour éric",True)
        debut_ecoute()
        contenu=""
        # Start streaming and recognize speech
        while True:
            data = stream.read(num_frames=4096,exception_on_overflow=False)#read in chunks of 4096 bytes
            if rec.AcceptWaveform(data):#accept waveform of input voice
                # Parse the JSON result and get the recognized text
                result = json.loads(rec.Result())
                recognized_text = result['text']
             
                if ("etude web" in recognized_text.lower()):
                    contenu_web:str=""
                    def enter_url()->str:
                        print("""
url complet de la page web étudier 
***********************************""")
                        lire_reponse("Veuillez entrer l'url complet de la page web étudier",True)
                        my_url=input("url: ")
                        if my_url=="" :
                            lire_reponse("erreur d'URL",True)
                            enter_url()
                        elif "quit"==my_url :
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
                        lire_reponse("Page web en attente de lecture...",False)
                        instruction = make_choice(lire_reponse)
                        # if choix=="1":
                        #     instruction="Fais moi un résumé court de ce texte ci-dessous ?"
                        # elif choix=="2":
                        #     instruction="Qui sont les auteurs et intervenants dans ce livre ?"
                        # elif choix=="3":
                        #     instruction="Quelles sont les principales idées qui se dégagent de ce texte ?"
                        # else : 
                        #     recognized_text=""
                        #     debut_ecoute()
                        #     break
                        if instruction=="quit" :
                            recognized_text=""
                            debut_ecoute()
                            break
                        
                        resumer_a_faire=instruction+"\n"+contenu_web
                        
                        lire_reponse("Question prise en compte en rapport avec le document, veuillez patienter...",False)
                        response2 = client.chat(model=MODEL,messages=[{'role': 'user','content':resumer_a_faire,},])
                        reponse2=response2["message"]["content"]
                        lire_reponse("Réponse trouvée..."+reponse2+"\nfin de la réponse...",True)
                        with open(resume_web_page, "w",encoding="utf-8") as resume_web:
                            resume_web.write(reponse2+"\n")   
                        recognized_text=""
                        debut_ecoute()
                    
                
                if ("fichiers texte" in recognized_text.lower()) or \
                    ("fichier texte" in recognized_text.lower()) or \
                    ("lire un fichier texte" in recognized_text.lower()) or \
                    ("télécharger un fichier texte" in recognized_text.lower()) or \
                    ("charger un fichier texte" in recognized_text.lower()) or \
                    ("télécharger un fichier" in recognized_text.lower()) :
                    my_file_name:str=""
                    contenu_du_fichier:str=""
                    def enter_name_file()->str:
                        print("""
Chemin complet du fichier à étudier 
***********************************                             
""")
                        lire_reponse("Veuillez entrer le chemin complet du fichier",True)
                        my_file_name=input(": ")
                        if my_file_name=="" :
                            lire_reponse("erreur de nom de fichier",True)
                            enter_name_file()
                        elif "quit"==my_file_name :
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
                        lire_reponse("Document en attente de lecture...",False)
                        instruction = make_choice(lire_reponse)
                        # if choix=="1":
                        #     instruction="Fais moi un résumé court de ce texte ci-dessous ?"
                        # elif choix=="2":
                        #     instruction="Qui sont les auteurs et intervenants dans ce livre ?"
                        # elif choix=="3":
                        #     instruction="Quelles sont les principales idées qui se dégagent de ce texte ?"
                        # else : 
                        #     recognized_text=""
                        #     debut_ecoute()
                        #     break
                        if instruction=="quit" : 
                            recognized_text=""
                            debut_ecoute()
                            break
                        
                        resumer_a_faire=instruction+"\n"+contenu_du_fichier
                        
                        lire_reponse("Question prise en compte en rapport avec le document, veuillez patienter...",False)
                        response2 = client.chat(model=MODEL,messages=[{'role': 'user','content':resumer_a_faire,},])
                        reponse2=response2["message"]["content"]
                        lire_reponse("Réponse trouvée..."+reponse2+"\nfin de la réponse...",True)
                        with open(resume_file_path, "w",encoding="utf-8") as resume_file:
                            resume_file.write(reponse2+"\n")   
                        recognized_text=""
                        debut_ecoute()
                    
             
                # Check for the termination keyword
                if "terminé" in recognized_text.lower() and contenu!="":
                    print("---------------------------------------------\nOk. Traitement...")

                    # On pose la question à lAi Ollama
                    print("Question à l'Ia::"+contenu)
                    print("Question en traitement, veuillez patienter...")
                    lire_reponse("Question en traitement, veuillez patienter...",False)
                    response = client.chat(model=MODEL,messages=[{'role': 'user','content': contenu,},])
                    # il retourne un texte que l'on va faire lire à pyttsx3
                    reponse = response["message"]["content"]
                    lire_reponse("Réponse trouvée...",True)
                    print(reponse)
                    with open(response_file_path, "w",encoding="utf-8") as response_file:
                        response_file.write(reponse+"\n")
                    lire_reponse(reponse+" \nfin de la réponse...",True)
                    contenu=""
                    recognized_text=""
                    debut_ecoute()

                if "arrêtez" in recognized_text.lower():
                    lire_reponse("d'accord, arrêt de la discussion...",False)
                    arret_ecoute()
                    lire_reponse("Aurevoir Eric, et à bientôt !",True)
                    break

                # Write recognized text to the file
                if recognized_text!="":
                    print("Prompt::"+recognized_text)
                    output_file.write(recognized_text + "\n")
                    contenu+=recognized_text+"\n"
                    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    engine.stop()
    # Terminate the PyAudio object
    p.terminate()


if __name__ == '__main__':
    main()