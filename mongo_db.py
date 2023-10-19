from motor import motor_asyncio

client = motor_asyncio.AsyncIOMotorClient('mongodb://root:example@localhost:27017')
db = client.short_link