import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TDA_FILE_PATH = os.getenv("TDA_FILE_PATH")
    GENERAL_RULES_FILE_PATH = os.getenv("GENERAL_RULES_FILE_PATH")
    GENERAL_PROCEDURES_FILE_PATH = os.getenv("GENERAL_PROCEDURES_FILE_PATH")
