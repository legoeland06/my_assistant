import vosk
import pyaudio
import json
import pyttsx3
import ollama
 
MODEL="wizardlm2"

client = ollama.Client(host='http://localhost:11434')
ollama.show(MODEL)
client_to_web = ollama.Client()


engine = pyttsx3.init()
voice = engine.getProperty('voices')[0] # the french voice
engine.setProperty(voice, 'french')
engine.setProperty('rate',200)

def lire_reponse(alire :str,validation:bool) :
    if validation : arret_ecoute()
    engine.say(alire)
    engine.runAndWait()
    engine.stop()
    
    # text-to-audio
    
    # with open('scenario.txt', 'r',encoding='utf-8') as file:
    #     data = file.read().rstrip()
    # engine.save_to_file(data , 'scenario.mp3')

def arret_ecoute():
    print("Arrêt de l'écoute")
    stream.stop_stream()
    
def debut_ecoute():
    print("Je vous écoute")
    lire_reponse("Je vous écoute",True)
    stream.start_stream()
    
def lire_fichier()->str:
    with open('recognized_text.txt', 'r',encoding='utf-8') as file:
        data_file = file.read().rstrip()
    data_file

# audio-to-text

# Here I have downloaded this model to my PC, extracted the files 
# and saved it in local directory
# Set the model path
model_path = "vosk-model-fr-0.22"
# Initialize the model with model-path
model = vosk.Model(model_path)

#if you don't want to download the model, just mention "lang" argument 
#in vosk.Model() and it will download the right  model, here the language is 
#US-English
#model = vosk.Model(lang="en-us")

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

# Open a text file in write mode using a 'with' block
with open(output_file_path, "w",encoding="utf-8") as output_file:
    print("Bienvenu dans mon chatbot audio !!! \nDites << TERMINER >> pour finir votre question\nEt dites << ARRETER >> pour fermer la discussion\n-------------------------------------------------")
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
                lire_reponse(reponse+" \nfin de la réponse...",True)
                contenu=""
                recognized_text=""
                debut_ecoute()

            if "arrêtez" in recognized_text.lower():
                lire_reponse("d'accord, arrêt de la discussion...",True)
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
