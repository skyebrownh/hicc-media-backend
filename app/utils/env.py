import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", verbose=True)

SUPABASE_URL = str(os.getenv("SUPABASE_URL"))
SUPABASE_API_KEY = str(os.getenv("SUPABASE_API_KEY"))
FAST_API_KEY = str(os.getenv("FAST_API_KEY"))
RAILWAY_DATABASE_URL = str(os.getenv("RAILWAY_DATABASE_URL"))