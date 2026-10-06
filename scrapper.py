import requests
import json
import csv
import pandas as pd
import html

PATH_TO_BRONZE = "./bronze"

def store_bronze(apiResult):
    df = pd.DataFrame(apiResult)
    for column in df:
        df[column] = df[column].map(html.unescape)
    df.to_csv(f'{PATH_TO_BRONZE}/questions.csv', encoding="utf-8", mode="a", header="false")


def get_50_results():
    return []

def run():
    while True:
        results = get_50_results()
        store_bronze()
        break
    print("prout")


if __name__ == "__main__":
    run()
