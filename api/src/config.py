import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / f"{os.getenv("BANCO_DB")}"

TORTOISE_CONFIG = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {
                "file_path": str(DB_PATH),
            },
        }
    },
    "apps": {
        "models": {
            "models": [
                "src.auth.models",
                "src.post.models",
                # "src.auth.models",
                # "src.posts.models",
            ],
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "UTC",
}

