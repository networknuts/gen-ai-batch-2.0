from typing import TypedDict, Dict

class AgentState(TypedDict):
    user_request: str
    plan: str
    files: Dict[str, str]
    review: str
    score: int
