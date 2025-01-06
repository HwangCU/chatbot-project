import os
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()

os.environ.get["SERPAPI_API_KEY"] = GoogleSearch.SERP_API_KEY

def find_index(questions):
    params = {
        "engine": "google",
        "q": questions[0],
        "num": "4"
    }

    return GoogleSearch(params).get_dict()