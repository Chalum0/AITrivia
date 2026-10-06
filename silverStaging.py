from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import os


load_dotenv()

PATH_TO_BRONZE = os.getenv("PATH_TO_BRONZE")
BRONZE_FILE_NAME = os.getenv("BRONZE_FILE_NAME")
PATH_TO_SILVER = os.getenv("PATH_TO_SILVER")
SILVER_FILE_NAME = os.getenv("SILVER_FILE_NAME")

if not os.path.exists(f"{PATH_TO_BRONZE}/{BRONZE_FILE_NAME}"):
    raise FileNotFoundError("Bronze file not found")
# if os.path.exists(f"{PATH_TO_SILVER}/{SILVER_FILE_NAME}"):
#     os.remove(f"{PATH_TO_SILVER}/{SILVER_FILE_NAME}")
# os.makedirs(f"{PATH_TO_SILVER}", exist_ok=True)


# df = pd.read_csv(f"{PATH_TO_BRONZE}/{BRONZE_FILE_NAME}")

def prepareResponses(pathToCsvFile):
    df = pd.read_csv(pathToCsvFile)
    for row in df:
        possible_answers = [df["correct_answer"], *df["incorrect_answers"]]
        
    
    


prepareResponses(f"{PATH_TO_BRONZE}/{BRONZE_FILE_NAME}")
# def askAI(dataframe):




# df.to_parquet(f"{PATH_TO_SILVER}/{SILVER_FILE_NAME}")
