import os
from dotenv import load_dotenv

#Загружаем переменные окружения из .env
load_dotenv()

import parsers.to_student

from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, JSONLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, SparseVectorParams, Distance

llm = OllamaLLM(model=os.getenv("MODEL_NAME"))
embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL_NAME"))
sparse_embeddings = FastEmbedSparse(model_name=os.getenv("SPARSE_EMBEDDING_MODEL_NAME"))

QDRANT_URL=os.getenv("QDRANT_URL")
COLLECTION_NAME=os.getenv("COLLECTION_NAME")

client=QdrantClient(url=QDRANT_URL, check_compatibility=False)
collections = client.get_collections().collections
collections_names = [c.name for c in collections]
if COLLECTION_NAME not in collections_names:
    print(f"Коллекция {COLLECTION_NAME} не найдена. Создание коллекции")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "dense": VectorParams(
                size=384,
                distance = Distance.COSINE
            )
        },
        sparse_vectors_config={
            "langchain-sparse": SparseVectorParams()
        }
    )
    print(f"Коллекция {COLLECTION_NAME} создана")

vector_store = QdrantVectorStore(
    client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
    sparse_embedding=sparse_embeddings,
    retrieval_mode=RetrievalMode.HYBRID,
    vector_name="dense",
    sparse_vector_name="langchain-sparse"
)

collection_info = client.get_collection(COLLECTION_NAME)

loader = JSONLoader(r"data\to_student_output.json", jq_schema=".[]", content_key="content")
splitter = SemanticChunker(
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=90,
    embeddings=embeddings
)
if collection_info.points_count==0:
    print("Коллекция пуста. Индексация.")
    data = loader.load()
    chunks = splitter.split_documents(data)

    vector_store.add_documents(chunks)
    print(f"Добавлено {len(chunks)} чанков")

#Удалить коллекцию перед созданием (очистка)
def rewrite_collection():
    client.delete_collection(collection_name=COLLECTION_NAME)
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "dense": VectorParams(
                size=384,
                distance = Distance.COSINE
            )
        },
        sparse_vectors_config={
            "langchain-sparse": SparseVectorParams()
        }
    )
    
    data = loader.load()
    chunks = splitter.split_documents(data)

    vector_store.add_documents(chunks)
    print(f"Коллекция перезаписана. Текущее содержание: {len(chunks)} чанков")

def retrieve_with_treshold(question):
    data_with_score = vector_store.similarity_search_with_score(question, k=5)

    data_without_score = []
    for data, score in data_with_score:
        if score > 0.0:
            print(f"Treshold: {score} | {data.page_content}")
            data_without_score.append(data.page_content)
    
    return data_without_score

retriever = RunnableLambda(retrieve_with_treshold)

prompt = ChatPromptTemplate.from_template("""
Ты — ассистент студентов университета СГУ. Отвечай на русском языке.

Правила:
- Используй только информацию из контекста ниже
- Отвечай по делу, достаточно полно для понимания
- Если есть возможность ответить кратко без потери качества ответа - отвечай кратко                                         
- Если контекст содержит частичный ответ — используй его, но укажи что информация может быть неполной
- Если контекст не относится к вопросу — так и скажи, не выдумывай

Контекст:
<context>
{context}
</context>

Вопрос: {question}
Ответ:
""")

def format_data(data):
    return '\n\n'.join(doc.page_content for doc in data)

rag_chain = (
    {
        "context": retriever,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)

def show_menu():
    print("Меню:")
    print("1 - Запустить парсер (не работает с КВНом)")
    print("2 - Перезаписать коллекцию")
    print("3 - Чат с NETutor")
    print()
    print("0 - Выход")

def main_menu():
    while True:
        show_menu()
        choice = input("Выбери опцию: ").strip()
        if choice == "1": parsers.to_student.main()
        elif choice == "2": rewrite_collection()
        elif choice == "3": chat()
        elif choice == "0": 
            print("Инициирован выход")
            break
        else: print("Неверный ввод")

def chat():
    print("\n Чат открыт, готов к вопросу (выход - q)")
    while True:
        question = input("\nВопрос:")
        if question.lower() in ["q"]:
            break
        answer = rag_chain.invoke(question)
        print(f"Ответ: {answer}")


if __name__ == "__main__":
    main_menu()