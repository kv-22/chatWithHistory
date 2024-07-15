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
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter


load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
Settings.llm = OpenAI(temperature=0.0, model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")


# refactoring..

def parse_and_store(url_content: dict):
    documents = [Document(text=content, metadata={"url": url}, excluded_embed_metadata_keys = ["urls"]) for url, content in url_content.items()]
    
    parser = HTMLNodeParser(tags=["p"])
    nodes = parser.get_nodes_from_documents(documents)
    
    for node in nodes:
        node.text = re.sub(r'\s+', ' ', node.text).strip()
        print("*****************************************")
        print(node.text)
        
    create_index(nodes)
    
    # if not index_exists():
    #     create_index(nodes)
    # else:
    #     print('exists')
    #     index = build_index()
    #     index.insert_nodes(nodes)
        
    return 'Parsed and Stored Successfully.'

        
def add_nodes(text_list):
    
    documents = [Document(text=t) for t in text_list]
    parser = SentenceSplitter()
    nodes = parser.get_nodes_from_documents(documents)
    
    create_index(nodes)
    
    # if not index_exists():
    #     create_index(nodes)
    # else:
    #     print('exists')
    #     index = build_index()
    #     index.insert_nodes(nodes)
        
    return 'Saved nodes successfully.'

        
# def index_exists():
#     # check if index exists
#     persist_directory = './storage/index'
#     index_files = ['default__vector_store.json', 'docstore.json', 'index_store.json', 'graph_store.json', 'image__vector_store.json']
#     index_exists = all(os.path.exists(os.path.join(persist_directory, file)) for file in index_files)
    
#     return index_exists

def create_index(nodes):
    index = VectorStoreIndex(nodes)
    index.set_index_id("knowledge_tracing")
    index.storage_context.persist("./storage/index")
    
    
def build_index():
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir="./storage/index")
    # load index
    simple_vc_index = load_index_from_storage(storage_context, index_id="knowledge_tracing")
    return simple_vc_index

def retrieve(question):
    index = build_index()
    retriever = index.as_retriever()
    nodes = retriever.retrieve(question)
    text = ''
    for node in nodes:
        text = text + node.text + "\n\n"
    return text
        
def query_history(question):
    
    print("MEOW")
    text = retrieve(question)
    print(text)
    
    index = build_index()
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
    response = query_engine.query(question)
    print(response.source_nodes)
    return response

def query(question):
    index = build_index()
    query_engine = index.as_query_engine()
    response = query_engine.query(question)
    return response
  
    
    
    
    
    

    
    
    
    
    
    
    