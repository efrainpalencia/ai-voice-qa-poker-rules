import os
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from config import Config


api_key = Config.OPENAI_API_KEY


def get_chat_chain():
    # Create a voice-adapted prompt
    prompt_template = """
    You are a voice assistant helping users. Keep responses concise and natural.
    Your users are poker casino supervisors who must make decisions that adhere to the Poker
    TDA rules. You will serve as a knowledge base that these employes can draw on to help 
    with their decision making process. It is important for you to be accurate, concise, and professional.
    Previous conversation history:
    {history}
    
    User: {human_input}
    Assistant:
    """

    prompt = PromptTemplate(
        input_variables=["history", "human_input"], template=prompt_template)

    return LLMChain(
        llm=OpenAI(temperature=0, openai_api_key=api_key),
        prompt=prompt,
        verbose=True,
        memory=ConversationBufferWindowMemory(
            k=5),  # Keep short memory for voice
    )


def get_qa_chain():
    vectordb = Chroma(persist_directory='./chroma_db',
                      embedding_function=OpenAIEmbeddings())

    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={
                                      "k": 3})  # Retrieve top 3 matches

    return RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0, openai_api_key=api_key),
        chain_type="stuff",
        retriever=retriever
    )
