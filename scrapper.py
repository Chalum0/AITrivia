from dotenv import load_dotenv
import ODBtoken as tk
import pandas as pd
import requests
import html
import json
import time
import csv
import os

load_dotenv()

token = os.getenv("OPENTDB_TOKEN")
tk.reset_token(token)

PATH_TO_BRONZE = "./bronze"
CSV_FILE_NAME = "questions.csv"
if os.path.exists(f"{PATH_TO_BRONZE}/{CSV_FILE_NAME}"):
    os.remove(f"{PATH_TO_BRONZE}/{CSV_FILE_NAME}")
os.makedirs(f"{PATH_TO_BRONZE}", exist_ok=True)

def store_bronze(apiResult):
    df = pd.DataFrame(apiResult)
    for column in df:
        df[column] = df[column].map(html.unescape)
    df.to_csv(f'{PATH_TO_BRONZE}/{CSV_FILE_NAME}', encoding="utf-8", mode="a", header="false")


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
        time.sleep(5.2)
    print("Saved data")


if __name__ == "__main__":
    run()
