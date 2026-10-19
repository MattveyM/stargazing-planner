from fastapi import FastAPI

app = FastAPI(title="Stargazing Planner API")

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the Stargazing Planner back end"}