from dotenv import load_dotenv
from pydantic import BaseModel
from openai import OpenAI
import pandas as pd
import random
import json
import time
import html
import ast
import os

load_dotenv()

PATH_TO_BRONZE = os.getenv("PATH_TO_BRONZE")
BRONZE_FILE_NAME = os.getenv("BRONZE_FILE_NAME")
PATH_TO_SILVER = os.getenv("PATH_TO_SILVER")
SILVER_FILE_NAME = os.getenv("SILVER_FILE_NAME")
MODEL = os.getenv("OPENAI_MODEL")

if not os.path.exists(f"{PATH_TO_BRONZE}/{BRONZE_FILE_NAME}"):
    raise FileNotFoundError("Bronze file not found")
if os.path.exists(f"{PATH_TO_SILVER}/{SILVER_FILE_NAME}"):
    os.remove(f"{PATH_TO_SILVER}/{SILVER_FILE_NAME}")
os.makedirs(f"{PATH_TO_SILVER}", exist_ok=True)


client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)

class Answer(BaseModel):
    answer: str


def clean_dataframe(dataframe):
    for index, row in dataframe.iterrows():
        dataframe["incorrect_answers"] = pd.Series(
            [
                ast.literal_eval(value) if isinstance(value, str) else value
                for value in dataframe["incorrect_answers"]
            ],
            index=dataframe.index,
            dtype=object,
        )
    return dataframe


def prepareResponses(pathToCsvFile):
    df = pd.read_csv(pathToCsvFile)
    df = clean_dataframe(df)

    for index, row in df.iterrows():
        start = time.time()
        incorrect_answers = row["incorrect_answers"]
        possible_answers = [
            html.unescape(answer)
            for answer in [row["correct_answer"], *incorrect_answers, "None"]
        ]
        question = html.unescape(row["question"])
        llm_response = ask_LLM(question, possible_answers)
        response_time = time.time() - start

        df.at[index, "llm_response"] = llm_response
        df.at[index, "llm_correct"] = (
            llm_response.lower() == html.unescape(row["correct_answer"]).lower()
        )
        df.at[index, "response_time"] = response_time
        print(f"Row: {index}, llm: {llm_response} : {llm_response.lower() == html.unescape(row['correct_answer']).lower()}")

    df.to_parquet(f"{PATH_TO_SILVER}/{SILVER_FILE_NAME}", index=False)


def ask_LLM(question, responses):
    responses = responses.copy()
    random.shuffle(responses)

    answer = client.responses.parse(
        model=MODEL,
        input=[
            {
                "role": "user",
                "content": f"Question : \n {question} \n\n Possible Answers: \n {responses}",
            }
        ],
        text_format=Answer,
        reasoning={"effort": "none"},
    )
    return str(answer.output_parsed.answer)






if __name__ == "__main__":
    prepareResponses(f"{PATH_TO_BRONZE}/{BRONZE_FILE_NAME}")
    # df = pd.read_csv(f"{PATH_TO_BRONZE}/{BRONZE_FILE_NAME}")



# df.to_parquet(f"{PATH_TO_SILVER}/{SILVER_FILE_NAME}")
