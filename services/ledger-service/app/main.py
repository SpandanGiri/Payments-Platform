from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def test():
    return {'msg':'ledger service is running'}
