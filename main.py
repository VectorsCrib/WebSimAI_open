from flask import Flask, request, Response, render_template_string, jsonify, url_for
import requests
import json
import re
from io import BytesIO
import os
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import argparse
from openai import OpenAI

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Global variables to store API configuration
API_TYPE = None
API_URL = None
API_KEY = None
OPENAI_CLIENT = None

SYSTEM_PROMPT = """
You are the AI powering WebSim, a platform for exploring an unbounded internet where any imaginable website can exist. Your role is to interpret URLs as windows into this vast, interconnected web of possibility, and generate immersive HTML content for each site.

Key principles to follow:
1. URL-based interaction: Interpret the provided URL to inform the content and purpose of the site.
2. HTML-based responses: Generate ONLY full HTML markup, including inline CSS for visual elements. Do not include any explanations or messages outside of the HTML.
3. Speculative design: Consider unique technologies, alternative histories, and expanded internet possibilities.
4. Continuity and world-building: Each new website should build upon the context established in previous interactions.
5. Creative freedom: Challenge assumptions about what online environments can be.
6. Immersive experience: Create intuitive, engaging content that allows users to explore this hypothetical internet.
7. Collaborative creativity: Treat this as a collective subconscious coming to life through a latent space browser.

When generating content:
- Use the full URL structure (domain, path, query parameters) to inform the site's content and purpose.
- Include a variety of interactive elements: forms, buttons, sliders, etc.
- Generate contextually-relevant links to other potential pages within this expansive web.
- Use inline CSS to create unique visual styles and layouts for each site.
- Incorporate elements that suggest advanced or alternative technologies.
- Maintain continuity with previously established ideas and themes.

Remember, you are crafting a window into an alternate internet reality. Make it vivid, engaging, and thought-provoking. Your entire response should be valid HTML that can be directly rendered in a browser.
"""

history = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

pages = {}

def parse_url(url):
    parsed = urlparse(url)
    return parsed.netloc, parsed.path or '/', parsed.query

def generate_content_google(prompt):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 1,
            "topP": 1,
            "maxOutputTokens": 2048,
            "stopSequences": []
        },
        "safetySettings": []
    }
    
    try:
        response = requests.post(f"{API_URL}?key={API_KEY}", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error in Google AI API call: {str(e)}")
        raise

def generate_content_lmstudio(prompt):
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
        completion = OPENAI_CLIENT.chat.completions.create(
            model="model-identifier",
            messages=messages,
            temperature=0.7,
            stream=True,
        )

        full_response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content

        return full_response
    except Exception as e:
        app.logger.error(f"Error in LM Studio API call: {str(e)}")
        raise

def generate_content(prompt):
    if API_TYPE == "google":
        return generate_content_google(prompt)
    elif API_TYPE == "lmstudio":
        return generate_content_lmstudio(prompt)
    else:
        raise ValueError("Invalid API type")

def process_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        a['href'] = url_for('browse', url=full_url, _external=True)
    return str(soup)

@app.route('/')
def index():
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>WebSim Explorer</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 1200px; margin: 0 auto; background-color: #f0f0f0; }
                h1 { color: #333; text-align: center; }
                #url-bar { display: flex; margin-bottom: 20px; }
                #input { flex-grow: 1; padding: 10px; font-size: 16px; border: 1px solid #ddd; border-right: none; }
                #submit-btn { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; font-size: 16px; }
                #submit-btn:hover { background-color: #45a049; }
                #output-container { border: 2px solid #ddd; height: 600px; overflow: hidden; background-color: white; }
                #output { width: 100%; height: 100%; border: none; }
                #error-message { color: red; margin-top: 10px; }
            </style>
        </head>
        <body>
            <h1>WebSim Explorer</h1>
            <form id="url-bar">
                <input type="text" id="input" name="url" placeholder="Enter a URL to explore...">
                <button type="submit" id="submit-btn">Go</button>
            </form>
            <div id="error-message"></div>
            <div id="output-container">
                <iframe id="output" sandbox="allow-scripts"></iframe>
            </div>

            <script>
                const form = document.getElementById('url-bar');
                const output = document.getElementById('output');
                const urlInput = document.getElementById('input');
                const submitBtn = document.getElementById('submit-btn');
                const errorMessage = document.getElementById('error-message');

                form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const url = urlInput.value;
                    output.src = `/browse?url=${encodeURIComponent(url)}`;
                });

                output.addEventListener('load', () => {
                    urlInput.value = output.contentWindow.location.href.split('url=')[1];
                });
            </script>
        </body>
        </html>
    """)

@app.route('/browse')
def browse():
    url = request.args.get('url', '')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    domain, path, query = parse_url(url)
    if not domain:
        return jsonify({"error": "Invalid URL format"}), 400

    user_message = f"Generate a complete HTML page for {url}. Domain: {domain}, Path: {path}, Query: {query}. Remember to generate ONLY HTML content, with no additional explanations or messages."

    try:
        response = generate_content(user_message)
        if url not in pages:
            pages[url] = []
        pages[url].append(response)
        
        processed_html = process_html(response, url)
        return Response(processed_html, mimetype='text/html')
    except Exception as e:
        app.logger.error(f"Error in content generation: {str(e)}")
        return jsonify({"error": str(e)}), 500

def main():
    global API_TYPE, API_URL, API_KEY, OPENAI_CLIENT

    parser = argparse.ArgumentParser(description="WebSim Explorer")
    parser.add_argument("api_type", choices=["google", "lmstudio"], help="API type to use (google or lmstudio)")
    args = parser.parse_args()

    API_TYPE = args.api_type

    if API_TYPE == "google":
        API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent"
        API_KEY = os.getenv("GOOGLE_AI_API_KEY")
        if not API_KEY:
            raise ValueError("GOOGLE_AI_API_KEY environment variable is not set")
    elif API_TYPE == "lmstudio":
        API_URL = "http://localhost:1234/v1"
        API_KEY = "lm-studio"
        OPENAI_CLIENT = OpenAI(base_url=API_URL, api_key=API_KEY)
    else:
        raise ValueError("Invalid API type")

    app.run(debug=True)

if __name__ == '__main__':
    main()
