import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))
from gerenciador_api_keys.recupera_api_key import get_api_key

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, ConversationChain
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType


def answer_simple_question(llm: OpenAI, question:str) -> str:
    llm.temperature = 0.9

    return llm(question)

def get_places_to_eat_using_prompt_template(llm: OpenAI, food: str) -> str:
    llm.temperature = 0.9

    prompt_template: PromptTemplate = PromptTemplate(
        input_variables=["food"],
        template="What are 5 vacation destinations for someone who likes to eat {food}",
    )

    prompt: str = prompt_template.format(food=food)

    return llm(prompt)

#Uma chain é uma combinação de um modelo de linguagem e um template de prompt
#É util para fazer várias chamadas sequenciais a um mesmo prompt de forma mais simples
#Usando-se a técnica anterior de usar um template de prompt, seria necessário fazer
#uma chamada a format e depois uma chamada a llm para cada item da lista.
def get_places_to_eat_using_chain(llm: OpenAI, foods_array: list) -> str:
    llm.temperature = 0.9

    prompt_template: PromptTemplate = PromptTemplate(
        input_variables=["food"],
        template="What are 5 vacation destinations for someone who likes to eat {food}",
    )

    chain: LLMChain = LLMChain(llm=llm, prompt=prompt_template)

    result: list = []
    for food in foods_array:
        print(f"Using chain to check good places to eat {food}")
        result.append(chain.run(food))
    
    return result

def get_current_info_using_agent(llm: OpenAI, questions: str) -> str:
    llm.temperature = 0

    tools = load_tools(["serpapi", "llm-math"], llm=llm)
    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    result = agent.run(questions)
    return result

class ChatMessage:
    def __init__(self, who: str, msg: str):
        self.who = who
        self.msg = msg
    
    def __str__(self):
        return f"{self.who}: {self.msg}"
    
def have_conversation(llm: OpenAI) -> list:

    llm.temperature = 0

    conversation = ConversationChain(llm=llm, verbose=True)
    chat_history = []

    next_message: ChatMessage = ChatMessage("Me", "Hi there!")
    chat_history.append(next_message)
    print(next_message)

    output = conversation.predict(input=next_message.msg)
    next_message = ChatMessage("Bot", output)
    chat_history.append(next_message)
    print(next_message)

    next_message = ChatMessage("Me", "I'm doing well! Just having a conversation with an AI.")
    chat_history.append(next_message)
    print(next_message)

    output = conversation.predict(input=next_message.msg)
    next_message = ChatMessage("Bot", output)
    chat_history.append(next_message)
    print(next_message)

    next_message = ChatMessage("Me", "What was the first think I said to you?")
    chat_history.append(next_message)
    print(next_message)

    output = conversation.predict(input=next_message.msg)
    next_message = ChatMessage("Bot", output)
    chat_history.append(next_message)
    print(next_message)

    next_message = ChatMessage("Me", "What is an alternative phrase for the first thing I said to you?")
    chat_history.append(next_message)
    print(next_message)

    output = conversation.predict(input=next_message.msg)
    next_message = ChatMessage("Bot", output)
    chat_history.append(next_message)
    print(next_message)

    return chat_history

class LangChainTest:

    def __init__(self, llm: OpenAI):
        self.llm = llm
    
    def test_answer_simple_question(self):
        question = "What are 5 vacation destinations for someone who likes to eat pasta?"
        print(f"Asking simple question: {question}")
        answer = answer_simple_question(self.llm, question)
        print(answer)

    def test_places_to_eat_using_prompt_template(self):
        print("Checking where to eat steak using prompt")
        answer = get_places_to_eat_using_prompt_template(self.llm, "steak")     
        print(answer)

    def test_places_to_eat_using_chain(self):
        print("Checking where to eat burritos and sushi using prompt")
        foods: list = ["burritos", "sushi"]
        answers = get_places_to_eat_using_chain(self.llm, foods)
        for i in range(0, len(answers)):
            print()
            print(f"Places to eat {foods[i]}: {answers[i]}") 

    def test_agent(self):
        question = "Who is the current king of England? What is the largest prime number that is smallest than his age?"
        print("Using agent to get current info about {question}")
        result = get_current_info_using_agent(llm, question) 
        print(result)

    def test_conversation(self):
        print("Having a conversation with an AI")
        chat_history = have_conversation(self.llm)
        print()
        print("Finished conversation, printing chat history:")
        for message in chat_history:
            print(message)

if __name__ == "__main__":

    os.environ["OPENAI_API_KEY"] = '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'#get_api_key("openai")
    os.environ["SERPAPI_API_KEY"] = '2ae744451d1287ed4b3f6c2b89b11cb934fb6115566c7d6dff70473dc6075cd8'#get_api_key("serp")
    #print(os.environ["OPENAI_API_KEY"])

    llm: OpenAI = OpenAI(temperature=0.9)

    option: int = None

    while(True):
        option_str: str = input("""
        1. Answer simple question
        2. Get places to eat using prompt template
        3. Get places to eat using chain
        4. Use agent to get current info from the internet and do math calculations
        5. Have a conversation with an AI

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

    llm_test = LangChainTest(llm)

    options = {
        1: llm_test.test_answer_simple_question,
        2: llm_test.test_places_to_eat_using_prompt_template,
        3: llm_test.test_places_to_eat_using_chain,
        4: llm_test.test_agent,
        5: llm_test.test_conversation
    }

    options[option]()