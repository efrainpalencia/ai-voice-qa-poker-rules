import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_openai.llms import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_chroma import Chroma
from langchain.schema.runnable import RunnableLambda, RunnableParallel, RunnableSequence
from app.config import Config

api_key = Config.OPENAI_API_KEY


def get_chat_chain():
    """Returns a conversational AI chat model."""
    prompt_template = """
    You are a voice assistant helping users. Keep responses concise and natural.
    Your users are poker casino supervisors who must make decisions that adhere to the Poker
    TDA rules. You will serve as a knowledge base that these employees can draw on to help 
    with their decision-making process. It is important for you to be accurate, concise, and professional.
    When you are aked a question, use the following resource to find the answer:
      https://www.pokertda.com/view-poker-tda-rules/. You may ask follow-up questions in order to find the answer.
    
    Previous conversation history:
    {history}
    
    User: {human_input}
    Assistant:
    """

    prompt = PromptTemplate(
        input_variables=["history", "human_input"], template=prompt_template)

    chat_chain = RunnableSequence(
        prompt | OpenAI(temperature=0, openai_api_key=api_key)
    ).with_config(memory=ConversationBufferWindowMemory(k=5))

    print("\n🔍 DEBUG: get_chat_chain() created RunnableSequence:\n", chat_chain)

    # Test invoking the chain with sample input
    test_input = {"history": "", "human_input": "What are the poker rules?"}
    try:
        response = chat_chain.invoke(test_input)
        print("\n✅ DEBUG: get_chat_chain() response:\n", response)
    except Exception as e:
        print("\n❌ ERROR: get_chat_chain() invocation failed:", e)

    return chat_chain


def get_qa_chain():
    """Returns a QA model using a Chroma vector store."""
    vectordb = Chroma(persist_directory='./chroma_db',
                      embedding_function=OpenAIEmbeddings())

    retriever = vectordb.as_retriever(
        search_type="similarity", search_kwargs={"k": 3})

    qa_chain = RunnableParallel(
        model=ChatOpenAI(temperature=0, openai_api_key=api_key),
        retriever=retriever
    )

    print("\n🔍 DEBUG: get_qa_chain() created RunnableParallel:\n", qa_chain)

    # Test invoking the chain with sample input
    test_query = {"query": "What happens if a player acts out of turn?"}
    try:
        response = qa_chain.invoke(test_query)
        print("\n✅ DEBUG: get_qa_chain() response:\n", response)
    except Exception as e:
        print("\n❌ ERROR: get_qa_chain() invocation failed:", e)

    return qa_chain


get_chat_chain()
get_qa_chain()
