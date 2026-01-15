from langchain.chat_models import init_chat_model
from tools import ask_human

tools = [ask_human]

llm = init_chat_model(
    model_provider="openai",
    model="gpt-4.1"
)

llm_with_tools = llm.bind_tools(tools=tools)
