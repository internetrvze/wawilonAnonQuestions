from aiosqlite import connect
from dotenv import load_dotenv
from os import getenv


load_dotenv()
DB_HOST = getenv('DATABASE_PATH')

