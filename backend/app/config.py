import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TDA_FILE_PATH = os.getenv("TDA_FILE_PATH")
    HWHR_FILE_PATH = os.getenv("HWHR_FILE_PATH")
