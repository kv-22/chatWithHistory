from fastapi import FastAPI
from pydantic import BaseModel
from rag_llama import parse_and_store, addNodes, retrieve, query, update_index
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

class Content(BaseModel):
    url_and_content: dict

class Notes(BaseModel):
    notes: list

class Question(BaseModel):
    question: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# refactoring..

@app.post("/parse")
async def get_parse(content: Content):
    url_and_content = content.url_and_content
    response = parse_and_store(url_and_content)
    return response
    
# old    
# @app.post("/add_nodes")
# async def add_nodes(text: Notes):
#     response = addNodes(text.notes)
#     return response

# new
@app.post("/add_nodes")
async def add_nodes(nodes: Content):
    response = addNodes(nodes.url_and_content)
    return response

@app.post("/retrieve")
async def retrieve_content(ques: Question):
    response = retrieve(ques.question)
    return {"message": "Retrieved successfully.", "answer": response}

@app.post("/query")
async def get_answer_general(ques: Question):
    response = query(ques.question)
    return {"message": "Chat completed successfully.", "answer": response}
    
# new endpoint for updating notes
@app.post("/update_nodes")
async def update_nodes(nodes: Content):
    response = update_index(nodes.url_and_content)
    return response  

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)