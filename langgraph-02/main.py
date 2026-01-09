from fastapi import FastAPI
from pydantic import BaseModel
from graph import build_graph

app = FastAPI(title="AI Website Builder")

graph_app = build_graph()


class WebsiteRequest(BaseModel):
    request: str


@app.post("/generate-website")
def generate_website(body: WebsiteRequest):
    result = graph_app.invoke({
        "user_request": body.request
    })

    return {
    "plan": result["plan"],
    "files": result["files"],
    "review": result["review"],
    "score": result["score"]
    }
