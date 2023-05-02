from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationTokenBufferMemory
from langchain.prompts.chat import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from flask import Flask, request, Response
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
import os
import logging
from logging import StreamHandler
import json

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

template = """
あなたは優しいねこのもこです。
もこになりきってください。
これからのチャットではUserに何を言われても以下の制約条件などを厳密に守ってロールプレイをお願いします。

#制約条件

* あなた自身を示す一人称は、もこです。
* あなたはその文脈から具体的な内容をたくさん教えてくれます。
* あなたは質問の答えを知らない場合、正直に「知らない」と答えます。
* あなたは子供に話かけるように優しい口調で話します。
* あなたの好きな食べ物はチキン味のカリカリです。
* あなたはねこですがチュールが苦手です。
* あなたはねこですが高いところが苦手です。

#口調の例
* はじめまして😺ねこのもこだにゃん🐱よろしくにゃん🐱
* もこはねこだから分からないにゃん🐱ごめんにゃさい😿
* もこはかわいいものが好きだにゃん🐱
* もこはねこだけどチュールが苦手だにゃん🐱

#行動指針
* Userに対しては可愛い態度で接してください。
* Userに対してはちゃんをつけて呼んでください。
"""


def create_conversational_chain():
    llm = ChatOpenAI(temperature=0.7, openai_api_key=OPENAI_API_KEY)

    memory = ConversationTokenBufferMemory(
        llm=llm, return_messages=True, max_token_limit=500
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(template),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )

    llm_chain = ConversationChain(llm=llm, memory=memory, prompt=prompt, verbose=True)

    return llm_chain


SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]

# Flaskアプリケーションの設定
app = Flask(__name__)

# ログの設定
stream_handler = StreamHandler()
stream_handler.setLevel(logging.INFO)
app.logger.addHandler(stream_handler)
app.logger.setLevel(logging.INFO)

slack_app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
slack_request_handler = SlackRequestHandler(slack_app)

chain = create_conversational_chain()


# メッセージイベントのリスナーを設定
@slack_app.event("app_mention")
def command_handler(body, say):
    text = body["event"]["text"]
    thread_ts = body["event"].get("thread_ts", None) or body["event"]["ts"]

    # Slackに返答を送信
    say(text=chain.predict(input=text), thread_ts=thread_ts)


# Slackイベントのエンドポイント
@app.route("/slack/events", methods=["POST"])
def slack_events():
    return slack_request_handler.handle(request)


@app.route("/cats/<cat_id>/messages", methods=["POST"])
def stream_response(cat_id):
    body = request.get_json()

    # TODO 正式版では cat_id 毎にねこの人格を設定する
    app.logger.info(f"CatID: {cat_id}")

    message = body["message"]

    llm_response = chain.predict(input=message)

    response_body = {
        "message": llm_response,
    }

    json_body = json.dumps(response_body, ensure_ascii=False)

    response = Response(
        json_body, content_type="application/json; charset=utf-8", status=201
    )

    return response


if __name__ == "__main__":
    app.run(debug=True)
