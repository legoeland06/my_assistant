# YourAssistant
![capture.png](capture_principale.png)

**Assistant conversationnel** 
Gestion de l'historique des conversations sur la session en cours (en RAM)
![capture.png](capture05.png)

# Use your local offline AI models
**using ollama server**

![capture.png](capture04.png)

# Use Groq api for online Ai Models
like llama-8b-8192, llama-70b-8192

![capture.png](capture02.png)

**Functionalities**

![capture.png](capture03.png)
* **listen**
  
    -> "salut"
  
    AI: "bonjour comment allez vous !"
   
* **speak**

    -> "Lis moi le contenu de ta dernière recherche"
  
    AI: "voici le contenu de ma dernière recherche : ...."
  
* **translate** (from *many* fo FR)
  
    -> click translate_button
  
    AI: texte traduit
  
* **_to_audio** (from txt to mp3)
  
    -> "transformation vers un fiohier mp3"
  
    AI: transformation terminée
  
* **loading TXT and PDF files**
  
    -> click importer un fichier TXT/PDF
  
    AI: "importation terminéee"
  
* **systemical prompts**
  
    -> click spéciality_button
  
  or
  
    -> "prépare moi un prompte sur ....."
  
  AI: résultat, un prompt prêt à l'emploi sur un LLM
  
* **web searching**
  
    -> "rechercher sur le web : something"
  
    AI : using google-search with an API-KEY
  
* **news scrapping from rrs feeds**
  
    -> "Afficher les actualités"
  
    AI : showing a window with list of actuality's categories
  
      the corresponding feed will be got when clicking in the list
  
**TODO**
Relier la gestion de l'historique à une base de données.
Etat des lieux : un résumé des anciennes conversation se lance automatiquement au bout de 15 discussions.
