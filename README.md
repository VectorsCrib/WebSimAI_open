# WebSimAI_open
 A local version of WebSim.AI, the prompt to webpage engine. Infinite possibilities to cure your boredom. ( I made it so you dont have to.... Youll thank me later)

Using Lm-Studio with this model "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF", I was able to get a decent output.

# Instructions:
1. ```pip3 install -r requirements.txt```
2. To run type `main.py lmstudio` and navigate to `http://127.0.0.1:5000` in your browser.
BAM! You should see the web interface.
Enjoy if you got issues let me know please...


# Docker:

Environment Variables for Initialization:
It is recommend to use environment variables to initialize the following parameters when using lm-studio:
API_URL: The URL for the API you’re interacting with.
API_KEY: Your API key for authentication.
model: The specific model you want to use.

Listening on 0.0.0.0:
To make the Flask application listen on all available network interfaces, set the host to 0.0.0.0 in your Flask app configuration.

Docker release:
build the Dockerfile and use CI/CD to make the docker image release.
