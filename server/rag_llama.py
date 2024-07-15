from llama_index.core import VectorStoreIndex, Document
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from dotenv import load_dotenv
import os
from llama_index.core import PromptTemplate
from llama_index.core.node_parser import HTMLNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
import re
from llama_index.core import get_response_synthesizer
import requests
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def generate_response(url_content:dict, question:str):
    load_dotenv()
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    Settings.llm = OpenAI(temperature=0.0, model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    documents = [Document(text=content, metadata={"url": url}, excluded_embed_metadata_keys = ["urls"]) for url, content in url_content.items()]
    
    parser = HTMLNodeParser(tags=["p"])
    nodes = parser.get_nodes_from_documents(documents)
    for node in nodes:
        node.text = re.sub(r'\s+', ' ', node.text).strip()
        print("*****************************************")
        print(node.text)

    index = VectorStoreIndex(nodes)
    
    template = (
        "Context information is below. \n"
        "---------------------\n"
        "{context_str}"
        "\n---------------------\n"
        "Given the context information and not prior knowledge, answer the query."
        "{query_str}\n"
        "Provide only the URLs of all the websites that answer the query. If none of the websites answer the query, return 'None'."
        "Answer:"
        )
    
    qa_template = PromptTemplate(template)
    
    query_engine = index.as_query_engine(text_qa_template=qa_template)
    # prompts_dict = query_engine.get_prompts()
    # print(prompts_dict['response_synthesizer:text_qa_template'])
    # print(prompts_dict['response_synthesizer:refine_template'])

    response = query_engine.query(question)
    
    print('source nodes')
    print(response.source_nodes)
    
    return response