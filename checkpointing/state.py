from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class SupportState(TypedDict):
    """
    LangGraph execution state.
    Persisted via MongoDB checkpointing.
    """
    messages: Annotated[list, add_messages]
