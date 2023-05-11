import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))
from gerenciador_api_keys.recupera_api_key import get_api_key

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

#Schemas - CHAT
#A função abaixo mostra uma mecanica possível para um chatbot com armazenamento do histórico da conversa
def basic_chat(chat: ChatOpenAI, initial_context:str, message: str) -> list:
    chat_history: list = [
        SystemMessage(content=initial_context),
        HumanMessage(content=message)
    ]

    response: AIMessage = chat(chat_history)
    chat_history.append(response)

    return chat_history

#A função abaixo mostra como retomar um chat com base em histórico. As respostas da IA podem ser reais ou "forjadas".
#Várias chamadas do método podem ser encadeadas para dar continuidade a um chat, enviando todo o histórico a cada vez
#Esse protocolo é necessário pois o chat é "stateless", a IA não tem como armazenar por conta própria o histórico
def chat_from_history(chat: ChatOpenAI, chat_history: list, new_message:str) -> list:
    #Create a copy of chat_history
    new_chat = chat_history.copy()
    new_chat.append(HumanMessage(content=new_message, example=False))
    response: AIMessage = chat(new_chat)
    new_chat.append(response)

    return new_chat

class LangChainTest:

    def __init__(self, chat: ChatOpenAI):
        self.chat = chat
    
    def test_basic_chat(self):
        #É possível antes de iniciar qualquer chat, dar o contexto sobre qual o papel que o bot deve desempenhar
        initial_context:str = "You are a nice AI bot that helps a user figure out what to eat in one short sentence"
        first_message:str = "I like tomatoes, what should I eat?"
        print(basic_chat(self.chat, initial_context, first_message))

    def test_chat_from_history(self):
        #O histórico do chat poderia ser lido de um banco de dados
        chat_history:list = [
            SystemMessage(content="You are a nice AI bot that helps a user figure out where to travel in one short sentence"),
            HumanMessage(content="I like the beaches where should I go?"),
            AIMessage(content="You should go to Nice, France")
        ]

        current_chat = chat_from_history(self.chat, chat_history, "What else should I do when I´m there?")
        print(current_chat)

        #Para continuar a conversa, passa o histórico atualizado e a próxima mensagem
        current_chat = chat_from_history(self.chat, current_chat, "Any night life suggestions?")
        #Imprime somente a última pergunta e a última resposta do bot
        print(current_chat[-2:])

if __name__ == "__main__":

    os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", get_api_key("openai"))

    openai_api_key:str = os.environ["OPENAI_API_KEY"] 
    chat = ChatOpenAI(temperature=.7, openai_api_key=openai_api_key)

    option: int = None

    while(True):
        option_str: str = input("""
        1. Basic Chat
        2. Chat from history

        Enter option: 
        """)

        try:
            option: int = int(option_str)
            if option in [1, 2, 3, 4, 5]:
                break
            else:
                print("Invalid option")
        except ValueError:
            print("Invalid option")

    llm_test = LangChainTest(chat)

    options = {
        1: llm_test.test_basic_chat,
        2: llm_test.test_chat_from_history
    }

    options[option]()