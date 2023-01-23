from dotenv import load_dotenv
import os
from requests import get

load_dotenv()

class Credentials:
    def __init__(self):
        self.client_ID = os.getenv("client_ID")
        self.client_SECRET = os.getenv("client_SECRET")
        self.redirect_url = os.getenv("redirect_url")

def download_file(url, file_path):
    reply = get(url, stream=True)
    with open(file_path, 'wb') as file:
        for chunk in reply.iter_content(chunk_size=1024): 
            if chunk:
                file.write(chunk)