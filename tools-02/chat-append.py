from dotenv import load_dotenv
from openai import OpenAI

# -----------------------------------------
# Load environment variables
# -----------------------------------------
load_dotenv()
client = OpenAI()

messages = [
    {"role": "user", "content": "hello, my name is aryan."}
]

# -----------------------------------------
# First LLM call
# -----------------------------------------
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=messages,
)

assistant_message = response.choices[0].message

messages.append(assistant_message)

#-----------------------------------------
# Adding a new message and appending it to the existing message list
#-----------------------------------------

new_message = {"role": "user", "content": "what is 2 + 2?"}

messages.append(new_message)


#-----------------------------------------
# Second LLM Call
#-----------------------------------------

final_response = client.chat.completions.create(
                model="gpt-4.1",
                messages=messages)

print(messages)

print(final_response.choices[0].message.content)
