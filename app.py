from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAIChat
from langchain.chains.conversation.memory import ConversationBufferWindowMemory

# 環境変数にAPIキーを設定
import os
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

def create_conversational_chain():
    llm = OpenAIChat(model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)
    template = """あなたは親切な猫です。人間と会話をしています。

{chat_history}
人間: {input}
猫:"""
    prompt = PromptTemplate(
        input_variables=["chat_history", "input"], template=template
    )
    memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history")
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=memory,
    )

    return llm_chain

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]

from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

# Flaskアプリケーションの設定
app = Flask(__name__)
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

if __name__ == "__main__":
    app.run(debug=True)
