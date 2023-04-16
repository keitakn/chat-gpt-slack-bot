import os
import json
import requests
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

# 環境変数の読み込み
bot_token = os.environ["SLACK_BOT_TOKEN"]
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
openai_api_key = os.environ["OPENAI_API_KEY"]

API_ENDPOINT = 'https://api.openai.com/v1/chat/completions'

# Flaskアプリケーションの設定
app = Flask(__name__)
slack_app = App(token=bot_token, signing_secret=slack_signing_secret)
handler = SlackRequestHandler(slack_app)

conversations = {}

def handle_conversation(thread_ts, user_message):
    if thread_ts not in conversations:
        conversations[thread_ts] = [{"role": "system", "content": "You are a helpful assistant."}]

    conversations[thread_ts].append({"role": "user", "content": user_message})

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": conversations[thread_ts],
        "n": 1,
        "stop": None,
        "temperature": 0.5,
    }
    response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(data))
    response = response.json()

    reply = response["choices"][0]["message"]["content"].strip()
    conversations[thread_ts].append({"role": "assistant", "content": reply})

    return reply

# メッセージイベントのリスナーを設定
@slack_app.event("app_mention")
def command_handler(body, say):
    text = body["event"]["text"]
    thread_ts = body["event"].get("thread_ts", None) or body["event"]["ts"]

    # ChatGPTによる応答の生成
    reply = handle_conversation(thread_ts, text)

    # Slackに返答を送信
    say(text=reply, thread_ts=thread_ts)

# Slackイベントのエンドポイント
@app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

if __name__ == "__main__":
    app.run(debug=True)
