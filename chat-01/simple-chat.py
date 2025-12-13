from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
client = OpenAI()

system_prompt = """You are a coding assistant AI. If the user ends up asking a non-coding question, 
then please straight up refuse the request"""

response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "how to make a cup of tea?"}
    ]
)

print(response.choices[0].message.content)
