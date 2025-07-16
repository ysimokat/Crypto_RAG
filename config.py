import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "ArgumentRx/1.0")
    
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL = "gpt-3.5-turbo"
    
    RETRIEVAL_TOP_K = 10
    FAISS_INDEX_PATH = "data/faiss_index"
    
    MAX_SOURCES_PER_ARGUMENT = 5
    ARGUMENT_MAX_LENGTH = 500