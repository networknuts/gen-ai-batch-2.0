from langchain_core.tools import tool
from langgraph.types import interrupt


@tool
def ask_human(query: str) -> str:
    """
    Pause execution and wait for a human response.
    State is checkpointed before interruption.
    """
    response = interrupt({"query": query})
    return response["data"]
