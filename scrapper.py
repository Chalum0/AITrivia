from dotenv import load_dotenv
from pathlib import Path
import ODBtoken as tk
import requests
import json
import os

load_dotenv()

token = os.getenv("OPENTDB_TOKEN")
tk.reset_token(token)


def store_bronze(blabla):
    pass
    # Foutre dans le CSV
    # Le csv doit etre dans un dossier bronze

def get_trivia() -> list:
    try:
        req = requests.get(
            "https://opentdb.com/api.php",
            params={"amount": 50, "token": token},
            timeout=30
        )
        req.raise_for_status()  # HTTP errors
        data = req.json()

        if data["response_code"] == 0:
            questions = data["results"]
            return questions
        else:
            return []


    except Exception as e:
        print(f"Error: {e}")
        return []




def run():
    while True:
        results = get_trivia()
        if not results:
            break
        store_bronze(results)
    print("Saved data")


if __name__ == "__main__":
    run()
