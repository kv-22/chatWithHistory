from fastapi import FastAPI
from pydantic import BaseModel
from rag_llama import generate_response
import uvicorn


class Content(BaseModel):
    url_and_content: dict
    question: str

app = FastAPI()

@app.post("/content")
async def get_answer(content: Content):
    url_and_content = content.url_and_content
    question = content.question
   
    print("Received")
    response = generate_response(url_and_content, question)
   
    # text=''
    # for key, value in url_and_content.items():
    #     text += "Website: " + key + "\n" + value + "\n\n"
    # print(text)
    
    print(response)
    
    # Return a response
    return {"message": "Processed successfully",
            "answer": response}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)