import os
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain.chains import RetrievalQA
from langchain_pinecone import PineconeVectorStore
from langchain_upstage import ChatUpstage
from langchain_upstage import UpstageEmbeddings
from pinecone import Pinecone, ServerlessSpec
from pydantic import BaseModel
from openai import AsyncOpenAI

load_dotenv()


vector_store = None

# upstage models
chat_upstage = ChatUpstage()
embedding_upstage = UpstageEmbeddings(model="embedding-query")

pinecone_api_key = os.environ.get("PINECONE_API_KEY")
pc = Pinecone(api_key=pinecone_api_key)
index_name = "galaxy-a35"

# create new index
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=4096,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

pinecone_vectorstore = PineconeVectorStore(index=pc.Index(index_name), embedding=embedding_upstage)

pinecone_retriever = pinecone_vectorstore.as_retriever(
    search_type='mmr',  # default : similarity(유사도) / mmr 알고리즘
    search_kwargs={"k": 3}  # 쿼리와 관련된 chunk를 3개 검색하기 (default : 4)
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class AssistantRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None


class ChatRequest(BaseModel):
    messages: List[ChatMessage]  # Entire conversation for naive mode


class MessageRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat_endpoint(req: MessageRequest):
    qa = RetrievalQA.from_chain_type(llm=chat_upstage,
                                     chain_type="stuff",
                                     retriever=pinecone_retriever,
                                     return_source_documents=True)

    result = qa(req.message)
    return {"reply": result['result']}

openai = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

async def create_vector_store():
    print("Creating vector store...")
    vector_store = await openai.beta.vector_stores.create(name="tourism sites")

        # Ready the files for upload to OpenAI
    file_paths = ["./서울시 관광 문화.json", "./서울시 관광 쇼핑.json", "./서울시 관광 음식.json", "./서울시 관광 자연.json", "./서울시 관광거리 정보 (한국어).json"]
    file_streams = [open(path, "rb") for path in file_paths]
    print("Uploading files...")

    # Use the upload and poll SDK helper to upload the files, add them to the vector store,
    # and poll the status of the file batch for completion.
    file_batch = await openai.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, 
        files=file_streams
    )
    print("File batch uploaded successfully")

    # You can print the status and the file counts of the batch to see the result of this operation.
    print(file_batch.status)
    print(file_batch.file_counts)




@app.post("/assistant")
async def assistant_endpoint(req: AssistantRequest):
    
    assistant = await openai.beta.assistants.retrieve("asst_RlG0py1ewx9wJnpONKJIijW5")

    assistant = await openai.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},)

    if req.thread_id:
        # We have an existing thread, append user message
        await openai.beta.threads.messages.create(
            thread_id=req.thread_id, role="user", content=req.message
        )
        thread_id = req.thread_id
    else:
        # Create a new thread with user message
        thread = await openai.beta.threads.create(
            messages=[{"role": "user", "content": req.message}]
        )
        thread_id = thread.id

    # Run and wait until complete
    await openai.beta.threads.runs.create_and_poll(
        thread_id=thread_id, assistant_id=assistant.id
    )

    # Now retrieve messages for this thread
    # messages.list returns an async iterator, so let's gather them into a list
    all_messages = [
        m async for m in openai.beta.threads.messages.list(thread_id=thread_id)
    ]
    print(all_messages)

    # The assistant's reply should be the last message with role=assistant
    assistant_reply = all_messages[0].content[0].text.value

    return {"reply": assistant_reply, "thread_id": thread_id}


@app.get("/health")
@app.get("/")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    create_vector_store()

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
