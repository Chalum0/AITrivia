from dotenv import load_dotenv
from pydantic import BaseModel
from openai import OpenAI
import pandas as pd
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

def ask_LLM(question, responses):
    answer = client.responses.parse(
        model=MODEL,
        input=[
            {
                "role": "user",
                "content": f"Question : \n {question} \n\n Possible Answer: \n {responses}",
            }
        ],
        text_format=Answer,
        reasoning={"effort": "none"},
    )
    return answer.output_parsed






if __name__ == "__main__":
    # df = pd.read_csv(f"{PATH_TO_BRONZE}/{BRONZE_FILE_NAME}")



# df.to_parquet(f"{PATH_TO_SILVER}/{SILVER_FILE_NAME}")
