import os
import getpass

from dotenv import load_dotenv
from serpapi import GoogleSearch
from langchain_community.utilities import SerpAPIWrapper

load_dotenv()

def find_index(questions):
    serpapi_api_key = os.getenv("SERPAPI_API_KEY")

    # SERPAPI KEY
    if not serpapi_api_key:
        GoogleSearch.SERP_API_KEY = getpass.getpass("Enter your SERPAPI API key: ")
        os.environ["SERPAPI_API_KEY"] = GoogleSearch.SERP_API_KEY

    params = {
        "engine": "google",
        "q": questions[0],
        "num": "4"
    }


    search = SerpAPIWrapper(params=params)
    search.run(questions[0])