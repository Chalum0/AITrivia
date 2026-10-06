import requests

def reset_token(t):
    req = requests.get(
        "https://opentdb.com/api_token.php",
        params={"command": "reset", "token": t},
        timeout=30
    )
    req.raise_for_status()
    data = req.json()
    if not data["response_code"] == 0:
        raise ConnectionError("Inable to reset Token")

def get_token():
    req = requests.get(
        "https://opentdb.com/api_token.php",
        params={"command": "request"},
        timeout=30
    )
    req.raise_for_status()
    data = req.json()
    if data["response_code"] != 0:
        print(f"Unable to generate token. Response code: {data['response_code']}")
    else:
        print(f"Token: {data["token"]}")

if __name__ == "__main__":
    get_token()
