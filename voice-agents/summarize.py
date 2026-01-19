# summarize.py
from openai import OpenAI

client = OpenAI()

def summarize(notes):
    prompt = f"""
You are a meeting assistant.

Summarize the meeting notes below.
Extract:
- Key discussion points
- Decisions
- Action items

Meeting Notes:
{notes}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    with open("meeting_notes.txt") as f:
        notes = f.read()

    summary = summarize(notes)
    print("\n📝 MEETING SUMMARY\n")
    print(summary)
