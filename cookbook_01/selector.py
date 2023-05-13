import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))
from gerenciador_api_keys.recupera_api_key import get_api_key

from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.llms import OpenAI

def use_selector(llm_davinci: OpenAI):
    openai_api_key:str = os.environ["OPENAI_API_KEY"] 

    # Examples of locations that nouns are found
    examples = [
        {"input": "pirate", "output": "ship"},
        {"input": "pilot", "output": "plane"},
        {"input": "driver", "output": "car"},
        {"input": "tree", "output": "ground"},
        {"input": "bird", "output": "nest"},
    ]

    # SemanticSimilarityExampleSelector will select examples that are similar to your input by semantic meaning

    #Para tornar um prompt mais eficiente ao ser enviado para o llm, é interessante usar exemplos
    #Ao invés de enviar os exemplos de forma hardcoded, é possível usar o langchain para, a partir de uma base ilimitada de exemplos
    #Tomar por base o input especificamente passado para o prompt (informado pelo usuário), fazer uma busca por similaridade em uma base
    #ilimitada de exemplos, e selecionar aqueles que tem mais relação com a palavra chave passada pelo usuário.
    #Para isso se usa o SemanticSimilarityExampleSelector, que é uma classe que seleciona exemplos semelhantes ao input do usuário.
    #Parametriza-se a classe com a base de exemplos, uma engine de embeddings, uma vector store e o número de exemplos que devem ser gerados
    #no prompt final que será enviado para o LLM.
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        # Examples é uma lista de dictionaries em que tanto as chaves quanto os valores são strings.
        # Cada exemplo é um dicionário com duas chaves: input e output.
        # O input é o exemplo que será passado para o llm, e o output é a resposta esperada.
        # o prompt template que será utilizado deverá usar as mesmas chaves para referenciar os valores.
        examples=examples, 
        
        # Precisa passar uma engine de embeddings para fazer busca por similaridade a partir dos exemplos.
        embeddings=OpenAIEmbeddings(openai_api_key=openai_api_key), 
        
        # VectorStore class
        # FAISS - Facebook AI Similarity Search. Representa a Vector Store a ser utilizada.
        # Uma alternativa é o Chroma. A classe de vector store armazenará os vectors de cada exemplo em memória.
        vectorstore_cls=FAISS, 
        
        # This is the number of examples to produce.
        k=2
    )

    #FewShotPromptTemplate é um tipo específico de template justamente para enviar, junto ao prompt, algums exemplos (Chamados shot examples)
    similar_prompt = FewShotPromptTemplate(
        # Opcionalmente pode-se passar a esse tipo de prompt um seletor de exemplos, e este poderá selecionar os exemplos mais apropriados
        # para o input do usuário. Uma alternativa menos desejável seria passar os exemplos hardcoded.
        #Usando-se o SemanticSimilarityExampleSelector é possível utiilzar o poder da similarity search em uma base vetorial. 
        example_selector=example_selector,
        
        # O prompt abaixo será usado para formatar os exemplos selecionados pelo example_selector ou passados hardcoded.
        # Com base nesse template, o prompt (String) final enviado ao LLM conterá a quantidade k de exemplos (Configurada no selector)
        # sendo cada exemplo formatado de acordo com o template abaixo.
        # Conclusão: As input variables devem ser coerentes com as chaves dos exemplos passados. No caso, input e output.
        example_prompt= PromptTemplate(
            input_variables=["input", "output"],
            template="Example Input: {input}\nExample Output: {output}",
        ),
        
        # Os parâmetros abaixo podem auxiliar a dar contexto ao LLM sobre os exemplos passados.
        #no caso abaixo "explica-se" ao LLM que a relação entre input e output é: Onde o input é usualmente encontrado?
        #Também deixa-se claro que o input é o input do usuário, e o output é a resposta esperada.
        prefix="Give the location an item is usually found in",
        suffix="Input: {noun}\nOutput:",
        
        # Quais variáveis deverão ser passadas na chamada de format deste prompt.
        input_variables=["noun"]
    )

    print('-' * 30)
    for example in examples:
        print(example['input'], " is usually found in ", example['output'])
    print('-' * 30)

    palavra_procurada = input("Com base nos exemplos acima, digite uma palavra para que o LLM indique onde usualmente é encontrada: ")

    prompt = similar_prompt.format(noun=palavra_procurada)
    #Abaixo imprime-se aquilo que será enviado ao LLM como prompt final.
    print("Enviando ao LLM o seguinte prompt:")
    print("-" * 30)
    print(prompt)
    print("-" * 30)
    print("Abaixo a resposta do LLM...")

    llm_response = llm_davinci(prompt)
    print(llm_response)


if __name__ == "__main__":

    os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", get_api_key("openai"))
    openai_api_key:str = os.environ["OPENAI_API_KEY"] 

    llm = OpenAI(model_name="text-davinci-003", openai_api_key=openai_api_key)

    use_selector(llm)
