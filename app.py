import requests
import os, signal
from flask import Flask, request
from openai import OpenAI
from icecream import ic

import google.generativeai as genai

app = Flask(__name__)

# This is API key for OpenAI
# openai.api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
# This is page access token that you get from facebook developer console.
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_TOKEN", "")
# This is API key for facebook messenger.
API = "https://graph.facebook.com/v20.0/me/messages?access_token=" + PAGE_ACCESS_TOKEN
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "")


@app.route("/gemini", methods=["GET"])
def verify():
    # Verify the webhook subscription with Facebook Messenger
    if request.args.get("hub.mode") == "subscribe" and request.args.get(
        "hub.challenge"
    ):
        if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return "Verification token missmatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world", 200


@app.route("/", methods=["POST"])
def fbwebhook():
    data = request.get_json()
    try:
        if data["entry"][0]["messaging"][0]["sender"]["id"]:
            message = data["entry"][0]["messaging"][0]["message"]
            sender_id = data["entry"][0]["messaging"][0]["sender"]["id"]
            chat_gpt_input = message["text"]
            print(chat_gpt_input)
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo-16k",
                messages=[{"role": "user", "content": chat_gpt_input}],
            )
            chatbot_res = completion.choices[0].message.content
            print("ChatGPT Response=>", chatbot_res)
            response = {
                "recipient": {"id": sender_id},
                "message": {"text": chatbot_res},
            }
            requests.post(API, json=response)
    except Exception as e:
        print(e)
        pass
    return "200 OK HTTPS."


@app.route("/gemini", methods=["POST"])
def fbwebhook_gemini():
    model = genai.GenerativeModel("gemini-1.5-flash")
    data = request.get_json()
    try:
        if data["entry"][0]["messaging"][0]["sender"]["id"]:
            # response = model.generate_content("")
            message = data["entry"][0]["messaging"][0]["message"]
            sender_id = data["entry"][0]["messaging"][0]["sender"]["id"]
            context = "context: NICO is Nabunturan Integrated Cooperative.\n limit the response to at least 3 sentences. use plain text as its a chatbot.\n"
            chat_gpt_input = context + message["text"]
            ic(message["text"])
            print(chat_gpt_input)
            # completion = client.chat.completions.create(
            #     model="gpt-3.5-turbo-16k",
            #     messages=[{"role": "user", "content": chat_gpt_input}],
            # )
            completion = model.generate_content(chat_gpt_input)
            # chatbot_res = completion.choices[0].message.content
            chatbot_res = completion.text
            print("Gemini Response=>", chatbot_res)
            response = {
                "recipient": {"id": sender_id},
                "message": {"text": chatbot_res},
            }
            requests.post(API, json=response)
    except Exception as e:
        print(e)
        pass
    return "200 OK HTTPS."


# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=5000)
