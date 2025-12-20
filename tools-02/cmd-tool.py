from dotenv import load_dotenv
from openai import OpenAI
import subprocess
import json
import os

# -----------------------------------------
# Load environment variables
# -----------------------------------------
load_dotenv()
client = OpenAI()

# -----------------------------------------
# Tool implementation (actual execution)
# -----------------------------------------
def run_cmd(cmd: str):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

# -----------------------------------------
# Tool schema (VERY IMPORTANT)
# -----------------------------------------
tools = [
    {
        "type": "function",
        "function": {
            "name": "run_cmd",
            "description": "Run a Linux shell command and return its output",
            "parameters": {
                "type": "object",
                "properties": {
                    "cmd": {
                        "type": "string",
                        "description": "Linux command to execute"
                    }
                },
                "required": ["cmd"]
            }
        }
    }
]

# -----------------------------------------
# System prompt
# -----------------------------------------
system_prompt = """
You are an assistant with access to a tool called run_cmd.
Based on the user's request, decide the correct Linux command.
Only call the tool when required.
"""




# -----------------------------------------
# User query
# -----------------------------------------
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "what is my current disk usage?"}
]

# -----------------------------------------
# First LLM call
# -----------------------------------------
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

assistant_message = response.choices[0].message

print(assistant_message)

# -----------------------------------------
# Handle tool call
# -----------------------------------------
if assistant_message.tool_calls:
    for tool_call in assistant_message.tool_calls:
        if tool_call.function.name == "run_cmd":
            args = json.loads(tool_call.function.arguments)
            output = run_cmd(args["cmd"])

            # Append tool result back into conversation
            messages.append(assistant_message)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": output
                }
            )

            # -----------------------------------------
            # Second LLM call (final response)
            # -----------------------------------------
            final_response = client.chat.completions.create(
                model="gpt-4.1",
                messages=messages
            )

            print(final_response.choices[0].message.content)
else:
    print(assistant_message.content)
