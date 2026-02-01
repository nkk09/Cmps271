from fastapi import FastAPI

app = FastAPI(title="AUB Reviews")

@app.get("/")
def root():
    return {"status": "ok"}