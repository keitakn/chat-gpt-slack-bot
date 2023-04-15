import os
from flask import Flask, request, jsonify
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
import openai

# 環境変数の読み込み
bot_token = os.environ["SLACK_BOT_TOKEN"]
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
openai.api_key = os.environ["OPENAI_API_KEY"]

# Flaskアプリケーションの設定
app = Flask(__name__)
slack_app = App(token=bot_token, signing_secret=slack_signing_secret)
handler = SlackRequestHandler(slack_app)

# メッセージイベントのリスナーを設定
@slack_app.event("app_mention")
def command_handler(body, say):
    text = body["event"]["text"]
    # ChatGPTによる応答の生成
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"{text}",
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.5,
    )
    # Slackに返答を送信
    reply = response.choices[0].text.strip()
    say(reply)

# Slackイベントのエンドポイント
@app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

if __name__ == "__main__":
    app.run(debug=True)
