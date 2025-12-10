import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", verbose=True)

FAST_API_KEY = str(os.getenv("FAST_API_KEY"))
RAILWAY_DATABASE_URL = str(os.getenv("RAILWAY_DATABASE_URL"))
LOCAL_TEST_DB_URL = str(os.getenv("LOCAL_TEST_DB_URL"))