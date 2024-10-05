import azure.functions as func

import fastapi

app = fastapi.FastAPI()

@app.get("/api")
async def index():
    return {
        "info": "Try /hello/Prateek for parameterized route.",
    }


@app.get("/hello/{name}")
async def get_name(name: str):
    return {
        "name": name,
    }
