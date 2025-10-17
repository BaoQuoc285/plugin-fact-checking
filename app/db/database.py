from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URL, MONGO_DB_NAME

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB_NAME]
