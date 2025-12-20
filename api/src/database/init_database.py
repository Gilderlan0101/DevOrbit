import os
from tortoise import Tortoise
from src.config import TORTOISE_CONFIG, DB_PATH
from dotenv import load_dotenv

load_dotenv()

async def init_database():
    await Tortoise.init(config=TORTOISE_CONFIG)

    # Apenas em desenvolvimento
    if os.getenv("ENVIRONMENT") != "production":
        await Tortoise.generate_schemas(safe=True)

    print(f"Banco pronto em: {DB_PATH}")


async def close_database():
    await Tortoise.close_connections()
