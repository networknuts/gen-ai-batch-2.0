from pymongo import MongoClient
from datetime import datetime

# ----------------------------------
# MongoDB connection
# ----------------------------------
client = MongoClient("mongodb://localhost:27017")
db = client["chat_db"]
collection = db["chat_history"]

# ----------------------------------
# Save a single message
# ----------------------------------
def save_message(thread_id: str, role: str, content: str):
    collection.insert_one({
        "thread_id": thread_id,
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow()
    })

# ----------------------------------
# Load full chat history
# ----------------------------------
def load_history(thread_id: str):
    cursor = collection.find(
        {"thread_id": thread_id}
    ).sort("timestamp", 1)

    return [
        {
            "role": doc["role"],
            "content": doc["content"]
        }
        for doc in cursor
    ]
