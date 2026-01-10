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
    # Step 1: Query MongoDB for all messages of this thread
    cursor = collection.find(
        {"thread_id": thread_id}
    )

    # Step 2: Sort messages by time (oldest → newest)
    cursor = cursor.sort("timestamp", 1)

    # Step 3: Prepare a list to store cleaned messages
    history = []

    # Step 4: Iterate over each document from MongoDB
    for doc in cursor:
        message = {
            "role": doc["role"],
            "content": doc["content"]
        }
        history.append(message)

    # Step 5: Return the full conversation history
    return history
