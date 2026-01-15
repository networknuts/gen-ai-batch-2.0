from dotenv import load_dotenv

load_dotenv()

DB_URI = "mongodb://admin:admin@localhost:27017"
THREAD_ID = "customer-123"

GRAPH_CONFIG = {
    "configurable": {
        "thread_id": THREAD_ID
    }
}
