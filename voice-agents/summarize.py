from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT_FILE = "system_prompt.txt"


def load_system_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def summarize(notes: str, system_prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"""
Meeting Notes:
{notes}
"""
            }
        ]
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    with open("meeting_notes.txt", "r", encoding="utf-8") as f:
        notes = f.read()

    system_prompt = load_system_prompt(SYSTEM_PROMPT_FILE)

    summary = summarize(notes, system_prompt)

    print("\nMEETING SUMMARY\n")
    print(summary)
