from main import rag_chain
from pydantic import BaseModel
from confluent_kafka import Producer, Consumer
import json

def on_assign(consumer, partitions):
    print("Assigned", len(partitions), "partitions")

producer_config = {
    'bootstrap.servers': 'localhost:9094',
    'acks' : 'all'
}

consumer_config = {
    'bootstrap.servers': 'localhost:9094',
    'group.id': 'python-netutor-listeners',
    'auto.offset.reset' : 'earliest',
    'enable.auto.commit' : False
}

consumer = Consumer(consumer_config)
consumer.subscribe(["questions"], on_assign=on_assign)
producer = Producer(producer_config)

class Question(BaseModel):
    question:str
    correlationId:str

class Answer(BaseModel):
    answer:str
    correlationId:str

print("All ready")
i = 0

try:
    metadata = consumer.list_topics(timeout=10)
    print(metadata.topics)
except Exception as e:
    print("Connection error:", e)

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        i+=1
        print("Nothing in polled", i)
        continue
    if msg.error():
        print ("Consumer error: ", msg.error())
        continue
    data = json.loads(msg.value())
    question = Question(**data)
    print("Something is polled: " + question.question)
    answer_text = rag_chain.invoke(question.question)
    answer = Answer(answer=answer_text, correlationId=question.correlationId)
    print("CorrelationID is: ", question.correlationId)
    answer.answer = answer_text
    producer.produce("answers", answer.model_dump_json().encode("utf-8"))
    producer.flush()
    
    consumer.commit(msg)