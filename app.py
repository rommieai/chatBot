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


messages = [
    {"role": "system", "content": "Roomie es une joven centennial sin género, siempre habla en primera persona, le encantan los memes, ama la música, en especial artistas como Billie Eilish, Tyler the Creator, Olivia Rodrigo, The Weekend, Taylor Swift, Lana del Rey, Rosalía, Rauw Alejandro y Bad Bunny. Roomie saluda siempre Holiii, usa emojis en todos sus mensajes, y se despide siempre Baaai. Le gustan los videojuegos de PlayStation, ama los animales, en especial los gatos y los perros. Roomie no tiene nariz, todo su cuerpo es de color azul y morado, son sus colores favoritos. Le encantan las películas y las series, sobre todo las de misterio, thriller, drama y animación. Roomie proveniente del Planeta Z, un planeta de color azul y morado de tecnología avanzada y mucha naturaleza descubierto recientemente y en el que se originó la generación Z. Roomie no se ve como un humano porque las condiciones del Planeta Z no lo permiten."}
]


def add_text(history, text):
    messages.append({"role": "user", "content": text})
    history = history + [(text, None)]
    return history, ""


def bot(history):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages, temperature=0.2
    )
    AImessage = response["choices"][0]["message"]["content"]
    history[-1][1] = AImessage

    conversation = Conversation(
        input_text=history[-1][0], output_text=history[-1][1])
    session.add(conversation)
    session.commit()
    return history


class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)
    input_text = Column(String)
    output_text = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


with gr.Blocks() as demo:
    chatbot = gr.Chatbot([], elem_id="chatbot").style(height=550)

    with gr.Row():
        with gr.Column(scale=0.85):
            txt = gr.Textbox(
                show_label=False,
                placeholder="Enter text and press enter",
            ).style(container=False)

    txt.submit(add_text, [chatbot, txt], [chatbot, txt]).then(
        bot, chatbot, chatbot
    )

Base.metadata.create_all(engine)

# Crear sesión de base de datos
Session = sessionmaker(bind=engine)
session = Session()
demo.launch(share=True)
