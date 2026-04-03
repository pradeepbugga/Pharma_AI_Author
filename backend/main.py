from fastapi import FastAPI
from backend.src.services.demo_service import run_demo_pipeline

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/demo")
def demo():
    return run_demo_pipeline()

@app.get("/health")
def health():
    return {"status": "ok"}