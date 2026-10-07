# AITrivia

AI is a simple project that aims to see what different AI models know by asking them trivia questions and comparing their output to a scrapped version of opentdb.com.

---
## Requirements
To install the requirements for this project:

### Linux/macos
```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows
```shell
python -m venv .venv
"./.venv/Scripts/activate"
pip install -r requirements.txt
```

---

## Evironment
To work with openTDB, you need to generate a token. For that:
```shell
python ODBtoken.py
```
Put this token in the .env :
```shell
cp .env.exemple .env
nano .env
```

---

## Bronze Layer
The first step is to fetch the content from the remote api. The goal is have every data in a csv file. For that:

```shell
python scrapper.py
```

This should run for a moment since the api only allows a call every 5 seconds. Progress should be displayed.

---

## Silver Layer
For that layer, the first step is fill out the environment variables for the openai api. 