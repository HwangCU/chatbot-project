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
from serpapi import GoogleSearch

load_dotenv()

os.environ["SERPAPI_API_KEY"] = os.environ.get("SERPAPI_API_KEY")

def search_web(questions):
    params = {
        "engine": "google",
        "q": questions,
        "num": "4"
    }

    return GoogleSearch(params).get_dict()


chat_upstage = ChatUpstage()
embedding_upstage = UpstageEmbeddings(model="embedding-query")

pinecone_api_key = os.environ.get("PINECONE_API_KEY")
pc = Pinecone(api_key=pinecone_api_key)
index_name = "galaxy-a35"

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


class AssistantRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None


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

@app.post("/assistant")
async def assistant_endpoint(req: AssistantRequest):
    # 웹 검색 수행
    search_results = search_web(req.message)
    
    # 검색 결과에서 relevant snippets 추출
    snippets = []
    if "organic_results" in search_results:
        for result in search_results["organic_results"][:3]:  # 상위 3개 결과만
            if "snippet" in result:
                snippets.append(result["snippet"])
    
    # 검색 결과를 포함한 향상된 프롬프트 생성
    enhanced_message = f"""질문: {req.message}
웹 검색 결과:
{' '.join(snippets)}

위의 웹 검색 결과를 참고하여 답변해 주세요."""
 
    assistant = await openai.beta.assistants.retrieve("asst_wTYWx8UcDs2QRG06kX6utDZV")

    if req.thread_id:
        await openai.beta.threads.messages.create(
            thread_id=req.thread_id, role="user", content=enhanced_message
        )
        thread_id = req.thread_id
    else:
        thread = await openai.beta.threads.create(
            messages=[{"role": "user", "content": enhanced_message}]
        )
        thread_id = thread.id

    await openai.beta.threads.runs.create_and_poll(
        thread_id=thread_id, assistant_id=assistant.id
    )

    all_messages = [
        m async for m in openai.beta.threads.messages.list(thread_id=thread_id)
    ]
    print(all_messages)

    assistant_reply = all_messages[0].content[0].text.value

    return {"reply": assistant_reply, "thread_id": thread_id}


@app.get("/")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
