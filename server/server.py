from fastapi import FastAPI
from pydantic import BaseModel
from rag_llama import parse_and_store, add_nodes, create_index, build_index, retrieve, query_history, query
import uvicorn


class Content(BaseModel):
    url_and_content: dict

class Notes(BaseModel):
    notes: list

class Question(BaseModel):
    question: str

app = FastAPI()


# refactoring..

@app.post("/parse")
async def get_parse(content: Content):
    url_and_content = content.url_and_content
    response = parse_and_store(url_and_content)
    return response

@app.post("/query_history")
async def get_answer_history(ques: Question):
    response = query_history(ques.question) # to query history because the prompt is different
    print(response)
    return {"message": "Chat comepleted successfully.", "answer": response}
    
    
@app.post("/add_nodes")
async def add_nodes(text: Notes):
    response = add_nodes(text.notes)
    return response

@app.get("/retrieve")
async def retrieve_content():
    response = retrieve()
    return {"message": "Retrieved successfully.", "answer": response}

@app.post("/query")
async def get_answer_general(ques: Question):
    response = query(ques.question) # for querying anything other than history
    return {"message": "Chat comepleted successfully.", "answer": response}
    
    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)