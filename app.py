import gradio as gr
import openai
import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('API_KEY_OPENIA')

db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB')
}

engine = create_engine(
    f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")
Base = declarative_base()
Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)
session = Session()

messages = []
prompt_global = ''


def add(history, text, prompt):
    global messages
    global prompt_global
    prompt_global = prompt
    if not messages:
        messages = [
            {"role": "system", "content": prompt_global}
        ]
    messages.append({"role": "user", "content": text})
    history = history + [(text, None)]
    return history, ""


def bot(history):

    global prompt_global
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages, temperature=0.2
    )
    print(prompt_global)
    AImessage = response["choices"][0]["message"]["content"]
    history[-1][1] = AImessage

    conversation = Conversation(
        input_text=history[-1][0], output_text=history[-1][1], prompt=prompt_global)
    session.add(conversation)
    session.commit()
    return history


class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)
    input_text = Column(String)
    output_text = Column(String)
    prompt = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


with gr.Blocks() as demo:
    chatbot = gr.Chatbot([], elem_id="chatbot").style(height=350)

    with gr.Row():
        with gr.Column(scale=0.85):
            txt = gr.Textbox(
                show_label=False,
                placeholder="Enter text and press enter",
            ).style(container=False)
            btn = gr.Button(value="Submit")
        with gr.Column(scale=0.85):
            inp = gr.Textbox(
                show_label=False,
                placeholder="Enter prompt",
            ).style(container=False)

    btn.click(add, [chatbot, txt, inp], [chatbot, txt]).then(
        bot, chatbot, chatbot
    )
    txt.submit(add, [chatbot, txt], [chatbot, txt]).then(
        bot, chatbot, chatbot
    )

demo.launch(share=True)
