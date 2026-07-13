from main import rag_chain
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Question(BaseModel):
    question:str
    correlationId:str

class Answer(BaseModel):
    answer:str
    correlationId:str


@app.post("/ask")
def ask(q: Question):
    answer_text = rag_chain.invoke(q.question)
    return Answer(answer=answer_text)