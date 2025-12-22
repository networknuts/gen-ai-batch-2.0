
# 🛠️ OpenAI Tool-Calling Example (Linux Command Execution)

This repository demonstrates how to build a **Python-based AI assistant** that can:

Accept a natural-language user query
Decide whether a **system command** needs to be executed
Safely invoke a local Linux command via a **tool call**
Feed the command output back to the LLM for a **final, user-friendly response**

The implementation uses OpenAI’s **function/tool calling**, environment variables via **dotenv**, and Python’s standard libraries.

---

## 📌 What This Script Does

At a high level, the script:

1. Loads environment variables (API keys, config)
2. Defines a **tool** (`run_cmd`) that executes Linux commands
3. Sends a user query to OpenAI
4. Lets the model decide whether to call the tool
5. Executes the tool locally if required
6. Sends the tool output back to the model
7. Prints the final, human-readable response

Example user query:

```
what is my current disk usage?
```

Behind the scenes, the model decides to run:

```
df -h
```

---

## 🧱 Project Structure

```
.
├── main.py        # Core script
├── .env           # Environment variables (not committed)
├── README.md      # Documentation
```

---

## 🔐 Environment Setup

### 1. Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install openai python-dotenv
```

### 3. Configure Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 📚 Libraries Used & Documentation

### 1. `python-dotenv`

Used to load environment variables from `.env`.

* Documentation:
  [https://pypi.org/project/python-dotenv/](https://pypi.org/project/python-dotenv/)
* Official Guide:
  [https://python-dotenv.readthedocs.io/](https://python-dotenv.readthedocs.io/)

---

### 2. `openai` (Python SDK)

Used to interact with OpenAI models and handle tool/function calling.

* Official Docs:
  [https://platform.openai.com/docs](https://platform.openai.com/docs)
* Python SDK Reference:
  [https://platform.openai.com/docs/api-reference](https://platform.openai.com/docs/api-reference)
* Tool / Function Calling Guide:
  [https://platform.openai.com/docs/guides/function-calling](https://platform.openai.com/docs/guides/function-calling)

---

### 3. `subprocess` (Standard Library)

Used to execute Linux shell commands safely from Python.

* Documentation:
  [https://docs.python.org/3/library/subprocess.html](https://docs.python.org/3/library/subprocess.html)

Key usage in this script:

```python
subprocess.run(
    cmd,
    shell=True,
    capture_output=True,
    text=True
)
```

---

### 4. `json` (Standard Library)

Used to parse the arguments returned by the tool call.

* Documentation:
  [https://docs.python.org/3/library/json.html](https://docs.python.org/3/library/json.html)

---

### 5. `os` (Standard Library)

Used implicitly for environment handling and OS-level interactions.

* Documentation:
  [https://docs.python.org/3/library/os.html](https://docs.python.org/3/library/os.html)

---

## 🧠 Understanding Tool Calling in This Script

### Tool Definition

```python
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
```

This schema **strictly defines** what the model is allowed to call.

---

### System Prompt

```text
You are an assistant with access to a tool called run_cmd.
Based on the user's request, decide the correct Linux command.
Only call the tool when required.
```

The system prompt is critical—it **governs tool usage discipline**.

---

### Two-Step LLM Interaction

1. **First call**
   The model decides whether a tool call is required.

2. **Second call**
   The tool output is sent back so the model can produce a final response.

This mirrors how **real AI agents** operate.

---

## ⚠️ Security Considerations (IMPORTANT)

This script executes **real shell commands**.

You MUST consider:

* ❌ Never expose this directly to untrusted users
* ❌ Do not allow arbitrary command execution in production
* ✅ Add allow-lists (e.g., only `df`, `ls`, `uptime`)
* ✅ Sanitize and validate commands
* ✅ Run inside containers or restricted users

For production systems, consider:

* Command allow-lists
* Sandboxing (Docker, Firecracker)
* RBAC-controlled tools

---

## 🧪 Example Output

> Your system is currently using approximately 46% of its root disk capacity.

---



