import redis
import time

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

job_id = input("Enter Job ID: ")

while True:
    result = redis_client.get(f"rag:response:{job_id}")
    if result:
        print("\n🤖 Answer:")
        print(result)
        break

    print("Waiting for response...")
    time.sleep(2)
