from openai import OpenAI
from state import AgentState
import re

ALLOWED_FILES = {
    "index.html",
    "src/main.tsx",
    "src/App.tsx",
    "src/index.css"
}


client = OpenAI()


def architect_plan(state: AgentState) -> AgentState:
    prompt = f"""
You are a senior frontend architect.

You MUST design the website using ONLY this stack:
- Vite
- React
- TypeScript
- Plain CSS

STRICT CONSTRAINTS:
- Frontend only (no backend, no APIs)
- No Next.js
- No server code
- No extra files

The implementation MUST map EXACTLY to these files:
- index.html
- src/main.tsx
- src/App.tsx
- src/index.css

User request:
{state['user_request']}

Produce a clear technical plan covering:
- Visual layout
- Component structure
- Styling approach
- UX intent
"""
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    state["plan"] = response.choices[0].message.content
    return state



import json

def coder(state: AgentState) -> AgentState:
    prompt = f"""
You are a senior frontend developer.

STRICT RULES:
- Output ONLY valid JSON
- No markdown
- No explanation
- No extra text
- Keys MUST be file paths
- Use ONLY these files:
  - index.html
  - src/main.tsx
  - src/App.tsx
  - src/index.css

Architecture plan:
{state['plan']}

Previous files (if any):
{state.get('files', {})}

Architect review feedback (if any):
{state.get('review', 'N/A')}

Return ONLY the JSON file map.
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        files = json.loads(raw_output)
    except json.JSONDecodeError:
        raise ValueError(f"Coder did not return valid JSON:\n{raw_output}")

    # Safety validation
    for path in files.keys():
        if path not in ALLOWED_FILES:
            raise ValueError(f"Illegal file generated: {path}")

    state["files"] = files
    return state


def architect_review(state: AgentState) -> AgentState:
    prompt = f"""
You are a senior frontend architect reviewing a website implementation.

Files:
{state['files']}

Evaluate on:
- Visual quality
- React best practices
- Code cleanliness
- UX clarity
- Production readiness

Return the response in this format ONLY:

Review:
<plain text feedback>

Score:
<integer from 1 to 10>
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content

    import re
    review_match = re.search(r"Review:(.*?)(Score:|$)", content, re.S)
    score_match = re.search(r"\b(10|[1-9])\b", content)

    if not score_match:
        raise ValueError(f"Invalid score in review:\n{content}")

    state["review"] = review_match.group(1).strip()
    state["score"] = int(score_match.group(1))
    return state
