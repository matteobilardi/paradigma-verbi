from dotenv import load_dotenv
import os


load_dotenv(os.path.dirname(__file__) + "/../.env")

MAIL_SERVER = os.environ.get("MAIL_SERVER")
MAIL_PORT = int(os.environ.get("MAIL_PORT"))
MAIL_USE_SSL = True if os.environ.get("MAIL_USE_SSL") == "true" else False
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = MAIL_USERNAME
MAIL_RECIPIENT_1 = os.environ.get("MAIL_RECIPIENT_1")
VERBIX_API_KEY = os.environ.get("VERBIX_API_KEY")
DEBUG = True if os.environ.get("DEBUG") == "true" else False
SECRET_KEY = os.environ.get("SECRET_KEY")

CACHE_CONFIG = {
    "CACHE_TYPE": "redis",
    "CACHE_REDIS_HOST": "localhost",
    "CACHE_REDIS_PORT": 6379,
    "CACHE_REDIS_DB": 0
}

NUM_WORDS_PER_ANALYSIS = 20
