import pathlib
import os

ROOT_FOLDER = pathlib.Path(__file__).parent

PORT = 8000
HOST = '0.0.0.0'
DEBUG = True

SECRET_KEY = os.urandom(24)

SQLITE_DB_PATH = ROOT_FOLDER / 'data.db'
