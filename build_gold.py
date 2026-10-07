import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

ROOT = os.getcwd()

subprocess.run(
    [
        "dbt",
        "run",
        "--project-dir", f"{ROOT}/src",
        "--profiles-dir", f"{ROOT}/src",
    ],
    cwd=ROOT,
    check=True,
)

print("Gold refreshed.")