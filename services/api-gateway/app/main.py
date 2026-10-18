from fastapi import FastAPI
from pydantic import BaseModel,Field


app = FastAPI()

@app.get("/health")
def test():
    return {'msg':'api-gateway is running'}



