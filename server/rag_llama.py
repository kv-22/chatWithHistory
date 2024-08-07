from llama_index.core import VectorStoreIndex, Document
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from dotenv import load_dotenv
import os
from llama_index.core.node_parser import HTMLNodeParser
import re
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.vector_stores.types import ExactMatchFilter, MetadataFilters
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.core.postprocessor import KeywordNodePostprocessor

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
Settings.llm = OpenAI(temperature=0.0, model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
Settings.embed_model = OpenAIEmbedding()

def parse_and_store(url_content: dict):
    documents = [Document(text=content, metadata={"url": url, "category": "history"}, excluded_embed_metadata_keys = ["url"]) for url, content in url_content.items()]
    
    parser = HTMLNodeParser(tags=["p"])
    nodes = parser.get_nodes_from_documents(documents)
    
    for node in nodes:
        node.text = re.sub(r'\s+', ' ', node.text).strip()
        node.text = truncate_text(node.text)
    
    
    # sentence window node parser to use after html parser
    sentence_window_node_parser = SentenceWindowNodeParser.from_defaults(
        window_size=3,
        window_metadata_key="window",
        original_text_metadata_key="original_text",)

    sentence_window_node_parser_nodes = sentence_window_node_parser(nodes)

    if not index_exists():
        create_index(sentence_window_node_parser_nodes)
    else:
        index = build_index()
        index.insert_nodes(sentence_window_node_parser_nodes)
        index.storage_context.persist(persist_dir="./storage/index")
        
    return 'Parsed and Stored Successfully.'

        
def addNodes(all_notes):
    documents = [Document(text=notes, id_ = url, metadata={"category": "note"}) for url, notes in all_notes.items()]
    parser = SentenceSplitter()
    nodes = parser.get_nodes_from_documents(documents)
    
    
    if not index_exists():
        create_index(nodes)
    else:
        index = build_index()
        index.insert_nodes(nodes)
        index.storage_context.persist(persist_dir="./storage/index")

    return 'Saved nodes successfully.'

def index_exists():
    # check if index exists
    persist_directory = './storage/index'
    index_files = ['default__vector_store.json', 'docstore.json', 'index_store.json', 'graph_store.json', 'image__vector_store.json']
    index_exists = all(os.path.exists(os.path.join(persist_directory, file)) for file in index_files)

    return index_exists

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
    filters = MetadataFilters(filters=[ExactMatchFilter(
        key="category", 
        value='note')])
    index = build_index()
    retriever = index.as_retriever(similarity_top_k=3, filters=filters)
    nodes = retriever.retrieve(question)
    print(nodes)
    text = ''
    for node in nodes:
        text = text + node.text + "\n\n"
    print(text)
    return text
        

def query(question):
    index = build_index()
    query_engine = index.as_query_engine(similarity_top_k=10, node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.75)])
    response = query_engine.query(question)
    print(response.source_nodes)
    
    url_list = [node.metadata['url'] for node in response.source_nodes if node.metadata['category']=='history']
    print(url_list)
    response_and_url = {'gpt_answer': response.response, 'urls': url_list}
    if url_list:
        return response_and_url
    else: 
        return response.response


# new update that should delete a note 
def update_index(id):
    index=build_index()
    index.delete_ref_doc(id, delete_from_docstore=True)
    index.storage_context.persist(persist_dir="./storage/index")
            
    return 'Updated successfully.'

def truncate_text(text, max_length=32000): # 8192 tokens each of 4 char is approx 32000
    if len(text) > max_length:
        truncated_text = text[:max_length]
        return truncated_text
    else:
        return text

# query that can be used with both notes and history
def query2(question):
    keywords = question.split()
    print(keywords)
    
    index = build_index()
    query_engine = index.as_query_engine(similarity_top_k = 20, node_postprocessors=[MetadataReplacementPostProcessor(target_metadata_key="window"), SimilarityPostprocessor(similarity_cutoff=0.75), KeywordNodePostprocessor(required_keywords=keywords)])
    response = query_engine.query(question)
    print(len(response.source_nodes))
    for node in response.source_nodes:
        # print(node.metadata['url'])
        # print(node.metadata['original_text'])
        print(node.text)
        print(node.score)
        print("\n\n")
    sources = [node.metadata['url'] if node.metadata['category'] == 'history' else node.text for node in response.source_nodes]
    
    original_list = sources
    unique_list = list(dict.fromkeys(original_list))
    
    # window = response.source_nodes[0].node.metadata["window"]
    # sentence = response.source_nodes[0].node.metadata["original_text"]

    # print(f"Window: {window}")
    # print("------------------")
    # print(f"Original Sentence: {sentence}")

    # print(sources)
    response_and_url = {'gpt_answer': response.response, 'sources': unique_list}
    if unique_list:
        return response_and_url
    else: 
        return response.response



    