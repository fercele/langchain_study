import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))
from gerenciador_api_keys.recupera_api_key import get_api_key

from langchain import PromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage, Document
from langchain.embeddings import OpenAIEmbeddings

#Schemas - TEXT (Igual ao primeiro teste de quickstart)

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

#Schemas - DOCUMENT
def use_document():
    document:Document = Document(page_content="This is my document. It is full of text that I've gathered from other places",
         metadata={
             'my_document_id' : 234234,
             'my_document_source' : "The LangChain Papers",
             'my_document_create_time' : 1680013019
         })
    
#Models
#Language Model - Explorado anteriormente - responder perguntas simples
#Chat Model - explorado acima
#Text Embedding Model
def use_text_embedding(embeddings: OpenAIEmbeddings):
    text = "Hi! It's time for the beach"
    text_embedding = embeddings.embed_query(text)
    print(f"Your embedding is length {len(text_embedding)}")
    print(f"Here's a sample: {text_embedding[:5]}...")

def use_prompt(davinci_llm: OpenAI):


    # I like to use three double quotation marks for my prompts because it's easier to read
    prompt = """
    Today is Monday, tomorrow is Wednesday.

    What is wrong with that statement?
    """

    print(prompt)

    response: str = davinci_llm(prompt)

    print(response)

def use_prompt_template(davinci_llm: OpenAI):
    
    # Notice "location" below, that is a placeholder for another value later
    template = """
    I really want to travel to {location}. What should I do there?

    Respond in one short sentence
    """

    prompt = PromptTemplate(
        input_variables=["location"],
        template=template,
    )

    final_prompt = prompt.format(location='Rome')

    print (f"Final Prompt: {final_prompt}")
    print ("-----------")
    print (f"LLM Output: {davinci_llm(final_prompt)}")

class LangChainTest:

    def __init__(self, chat: ChatOpenAI, embeddings: OpenAIEmbeddings, davinci_llm: OpenAI):
        self.chat = chat
        self.embeddings = embeddings
        self.davinci_llm = davinci_llm
    
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
    
    def test_text_embedding(self):
        use_text_embedding(self.embeddings)

    def test_prompt(self):
        use_prompt(self.davinci_llm)
    
    def test_prompt_template(self):
        use_prompt_template(self.davinci_llm)

if __name__ == "__main__":

    os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", get_api_key("openai"))

    openai_api_key:str = os.environ["OPENAI_API_KEY"] 
    chat = ChatOpenAI(temperature=.7, openai_api_key=openai_api_key)
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    davinci_llm = OpenAI(model_name="text-davinci-003", openai_api_key=openai_api_key)

    option: int = None

    while(True):
        option_str: str = input("""
        1. Basic Chat
        2. Chat from history
        3. Text Embedding
        4. Prompt with da vinci,
        5. Prompt Template with da vinci
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

    llm_test = LangChainTest(chat, embeddings, davinci_llm)

    options = {
        1: llm_test.test_basic_chat,
        2: llm_test.test_chat_from_history,
        3: llm_test.test_text_embedding,
        4: llm_test.test_prompt,
        5: llm_test.test_prompt_template

    }

    options[option]()