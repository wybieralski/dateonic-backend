from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.allowed_origins = ["http://localhost:3000"]
        self.model_name = "gpt-4"

settings = Settings()