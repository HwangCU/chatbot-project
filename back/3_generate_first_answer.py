# yes가 2개 이상일 경우, 질문과 함께 LLM에 입력하여 답변을 획득합니다.
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_upstage import ChatUpstage

def generate_first_answer(docs, user_question):
    # Prompt
    system = """
    Answer the question based on context.
    """
    user = """
    Question: {question}
    Context: {context}

    <<<Output Format>>>
    `Answer: <Answer based on the document.>`
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", user),
        ]
    )

    # LLM & Chain
    llm = ChatUpstage()
    rag_chain = prompt | llm | StrOutputParser()

    generation = rag_chain.invoke({"context": "\n\n".join(docs), "question": user_question})
    generation = generation.split(":")[1].strip() if ":" in generation else generation.strip()
    print(generation)