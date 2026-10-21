
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("NEXUS_DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("NEXUS_DATABASE_URL is missing from the .env file.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


def check_database_connection() -> bool:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
