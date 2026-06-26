import os
from dotenv import load_dotenv

#Загружаем переменные окружения из .env
load_dotenv()
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

llm = OllamaLLM(model=os.getenv("MODEL_NAME"))

embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL_NAME"))

QDRANT_URL=os.getenv("QDRANT_URL")
COLLECTION_NAME=os.getenv("COLLECTION_NAME")

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
client=QdrantClient(url=QDRANT_URL, check_compatibility=False)

#Удалить коллекцию перед созданием (очистка)
client.delete_collection(collection_name=COLLECTION_NAME)

collections = client.get_collections().collections
collections_names = [c.name for c in collections]

if COLLECTION_NAME not in collections_names:
    print(f"Коллекция {COLLECTION_NAME} не найдена. Создание коллекции")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,
            distance = Distance.COSINE
        )
    )
    print(f"Коллекция {COLLECTION_NAME} создана")

vector_store = QdrantVectorStore(
    client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
)

collection_info = client.get_collection(COLLECTION_NAME)
if collection_info.points_count==0:
    print("Коллекция пуста. Индексация.")

    loader = TextLoader(r"data\test_data.txt", encoding="utf-8")
    data = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20
    )
    chunks = splitter.split_documents(data)

    vector_store.add_documents(chunks)
    print(f"Добавлено {len(chunks)} чанков")

def retrieve_with_treshold(question):
    data_with_score = vector_store.similarity_search_with_score(question, k=5)

    data_without_score = []
    for data, score in data_with_score:
        if score > 0.3:
            print(f"Treshold: {score} | {data}")
            data_without_score.append(data)
    
    return data_without_score

retriever = RunnableLambda(retrieve_with_treshold)

prompt = ChatPromptTemplate.from_template("""
Ты — ассистент университета. Отвечай на вопрос, используя только контекст.
Если в контексте нет ответа — скажи: "Не знаю".

Контекст:
{context}

Вопрос: {question}

Ответ:
""")

def format_data(data):
    return '\n\n'.join(doc.page_content for doc in data)

rag_chain = (
    {
        "context": retriever | format_data,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)


if __name__ == "__main__":
    print("\n Чат открыт, готов к вопросу (выход - q)")
    while True:
        question = input("\nВопрос:")
        if question.lower() in ["q"]:
            break
        answer = rag_chain.invoke(question)
        print(f"Ответ: {answer}")