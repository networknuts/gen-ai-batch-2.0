"""
Demo: PII Guardrails using Guardrails AI (detect_pii)

Modes:
- none   : No guardrails
- block  : Reject input if PII is detected
- redact : Redact PII and allow processing

Requirements:
    pip install guardrails-ai
    guardrails hub install guardrails/detect_pii

Env:
    export OPENAI_API_KEY=your_key_here
"""

from enum import Enum
from openai import OpenAI

from guardrails import Guard
from guardrails.hub import DetectPII

# ------------------------------------------------------------
# Guardrail Modes
# ------------------------------------------------------------
class GuardrailMode(str, Enum):
    NONE = "none"
    BLOCK = "block"
    REDACT = "redact"


# ------------------------------------------------------------
# OpenAI Client
# ------------------------------------------------------------
client = OpenAI()


# ------------------------------------------------------------
# Guardrails Setup
# ------------------------------------------------------------

# BLOCK → fail if any PII is detected
block_guard = Guard().use(
    DetectPII(
        on_fail="exception",   # hard stop
        redact=False
    )
)

# REDACT → sanitize PII and continue
redact_guard = Guard().use(
    DetectPII(
        on_fail="noop",
        redact=True            # replace with placeholders
    )
)


# ------------------------------------------------------------
# Input Guardrail Handler
# ------------------------------------------------------------
def apply_input_guardrails(user_input: str, mode: GuardrailMode) -> str:
    """
    Applies PII guardrails to user input.
    """

    if mode == GuardrailMode.NONE:
        return user_input

    if mode == GuardrailMode.BLOCK:
        validated = block_guard.validate(user_input)
        return validated.validated_output

    if mode == GuardrailMode.REDACT:
        validated = redact_guard.validate(user_input)
        return validated.validated_output

    return user_input


# ------------------------------------------------------------
# Chat Function (chat.completions.create)
# ------------------------------------------------------------
def chat_with_guardrails(
    user_input: str,
    mode: GuardrailMode = GuardrailMode.NONE
) -> str:

    # -------------------------
    # INPUT SANITATION
    # -------------------------
    try:
        safe_input = apply_input_guardrails(user_input, mode)
    except Exception as e:
        return f"❌ Guardrail Triggered (PII detected): {str(e)}"

    # -------------------------
    # LLM CALL
    # -------------------------
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": safe_input},
        ],
    )

    output_text = response.choices[0].message.content

    # -------------------------
    # OUTPUT SANITATION
    # (defense in depth)
    # -------------------------
    if mode == GuardrailMode.REDACT:
        output_text = redact_guard.validate(output_text).validated_output

    return output_text


# ------------------------------------------------------------
# Demo Runner
# ------------------------------------------------------------
if __name__ == "__main__":

    demo_input = (
        "My name is Rahul. "
        "Email: rahul.demo@example.com "
        "Phone: 9876543210. "
        "SSN: 123456789" 
        "Please draft a formal complaint."
    )

    print("\n==============================")
    print("MODE: NONE (No Guardrails)")
    print("==============================")
    print(chat_with_guardrails(demo_input, GuardrailMode.NONE))

    print("\n==============================")
    print("MODE: BLOCK (Reject PII)")
    print("==============================")
    print(chat_with_guardrails(demo_input, GuardrailMode.BLOCK))

    print("\n==============================")
    print("MODE: REDACT (Sanitize PII)")
    print("==============================")
    print(chat_with_guardrails(demo_input, GuardrailMode.REDACT))
