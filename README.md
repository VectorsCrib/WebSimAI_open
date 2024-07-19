# WebSimAI_open
 A local version of WebSim.AI, the prompt to webpage engine. Infinite possibilities to cure your boredom. ( I made it so you dont have to.... Youll thank me later)

Using Lm-Studio with this model "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF", I was able to get a decent output.

# Instructions:
1. ```pip3 install -r requirements.txt```
2. To run type `main.py lmstudio` and navigate to `http://127.0.0.1:5000` in your browser.
BAM! You should see the web interface.
Enjoy if you got issues let me know please...


# Docker:
As the owner of this repo I dont know docker. But dont let my lack of knowledge stop you. Heres a guide from the github user: genwch.
Environment Variables for Initialization:

1. ```API_URL```: The URL for the API you’re interacting with.
2. ```API_KEY:``` Your API key for authentication.
3. ```model```: The specific model you want to use.

# Listening on 0.0.0.0:
To make the Flask application listen on all available network interfaces, set the host to 0.0.0.0 in your Flask app configuration.

# Docker release:
build the Dockerfile and use CI/CD to make the docker image release.
