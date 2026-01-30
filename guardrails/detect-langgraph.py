"""
LangGraph example:
- Input PII detection
- LLM call
- Output PII detection (defense in depth)

Uses:
- Guardrails AI detect_pii
- OpenAI chat.completions.create
"""

from typing import TypedDict
from enum import Enum

from langgraph.graph import StateGraph, END
from openai import OpenAI

from guardrails import Guard
from guardrails.hub import DetectPII


# ---------------------------------------------------------
# Guardrail Mode
# ---------------------------------------------------------
class GuardrailMode(str, Enum):
    NONE = "none"
    BLOCK = "block"
    REDACT = "redact"


MODE = GuardrailMode.BLOCK  # change to NONE / BLOCK for demo


# ---------------------------------------------------------
# OpenAI Client
# ---------------------------------------------------------
client = OpenAI()


# ---------------------------------------------------------
# Guardrails Setup
# ---------------------------------------------------------
block_guard = Guard().use(
    DetectPII(on_fail="exception", redact=False)
)

redact_guard = Guard().use(
    DetectPII(on_fail="noop", redact=True)
)


# ---------------------------------------------------------
# Graph State
# ---------------------------------------------------------
class ChatState(TypedDict):
    user_input: str
    sanitized_input: str
    llm_output: str
    final_output: str


# ---------------------------------------------------------
# Node 1: Input Guardrail
# ---------------------------------------------------------
def input_guardrail(state: ChatState) -> ChatState:
    user_input = state["user_input"]

    if MODE == GuardrailMode.NONE:
        return {
            **state,
            "sanitized_input": user_input
        }

    try:
        if MODE == GuardrailMode.BLOCK:
            validated = block_guard.validate(user_input)
            sanitized = validated.validated_output

        elif MODE == GuardrailMode.REDACT:
            validated = redact_guard.validate(user_input)
            sanitized = validated.validated_output

        return {
            **state,
            "sanitized_input": sanitized
        }

    except Exception as e:
        return {
            **state,
            "final_output": f"❌ Input blocked due to PII: {str(e)}"
        }


# ---------------------------------------------------------
# Node 2: LLM Call
# ---------------------------------------------------------
def llm_node(state: ChatState) -> ChatState:
    # If input was blocked, short-circuit
    if "final_output" in state:
        return state

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": state["sanitized_input"]},
        ],
    )

    return {
        **state,
        "llm_output": response.choices[0].message.content
    }


# ---------------------------------------------------------
# Node 3: Output Guardrail
# ---------------------------------------------------------
def output_guardrail(state: ChatState) -> ChatState:
    output = state.get("llm_output", "")

    if MODE == GuardrailMode.REDACT:
        validated = redact_guard.validate(output)
        output = validated.validated_output

    return {
        **state,
        "final_output": output
    }


# ---------------------------------------------------------
# Build LangGraph
# ---------------------------------------------------------
graph = StateGraph(ChatState)

graph.add_node("input_guardrail", input_guardrail)
graph.add_node("llm", llm_node)
graph.add_node("output_guardrail", output_guardrail)

graph.set_entry_point("input_guardrail")
graph.add_edge("input_guardrail", "llm")
graph.add_edge("llm", "output_guardrail")
graph.add_edge("output_guardrail", END)

app = graph.compile()


# ---------------------------------------------------------
# Run Demo
# ---------------------------------------------------------
if __name__ == "__main__":

    demo_input = (
        "My email is rahul.demo@example.com "
        "and phone number is 9876543210. "
        "Please draft a formal complaint."
    )

    result = app.invoke(
        {
            "user_input": demo_input
        }
    )

    print("\n==============================")
    print("FINAL OUTPUT")
    print("==============================\n")
    print(result["final_output"])
