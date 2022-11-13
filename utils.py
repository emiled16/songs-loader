from dotenv import load_dotenv
import os

load_dotenv()

class Credentials:
    def __init__(self):
        self.client_ID = os.getenv("client_ID")
        self.client_SECRET = os.getenv("client_SECRET")
        self.redirect_url = os.getenv("redirect_url")