import motor.motor_asyncio
from app.core.config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
master_db = client[settings.MASTER_DB]

# convenience collections
orgs_collection = master_db["organizations"]    # stores org metadata
admins_collection = master_db["admins"]        # stores admin user records
