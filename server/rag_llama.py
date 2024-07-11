from llama_index.core import VectorStoreIndex, Document
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from dotenv import load_dotenv
import os
from llama_index.core import PromptTemplate

def generate_response(url_content:dict, question:str):
    load_dotenv()
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    Settings.llm = OpenAI(temperature=0.2, model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
    documents = [Document(text=content, metadata={"url": url}) for url, content in url_content.items()]
    index = VectorStoreIndex.from_documents(documents) # chunks and creates embeddings
        
    template = (
        "Context information is below. \n"
        "---------------------\n"
        "{context_str}"
        "\n---------------------\n"
        "Given the context information and not prior knowledge, answer the query."
        "{query_str}\n"
        "Provide only the URLs of the websites that answer the query. If none of the websites answer the query, return 'None'."
        "Answer:"
        )
    
    qa_template = PromptTemplate(template)
    
    retriever = VectorIndexRetriever(index=index,similarity_top_k=10) #
   
    # nodes=retriever.retrieve(question)
    # for node in nodes:
    #     print(node.text)
    #     print('\n\n')
        
    query_engine = RetrieverQueryEngine.from_args(retriever, response_mode='refine', text_qa_template=qa_template) #
    
    response = query_engine.query(question)
    

    # print(response.source_nodes)
    return response
