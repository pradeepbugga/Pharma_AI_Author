from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.src.services.demo_service_stream import run_demo_pipeline_stream
import json

app = FastAPI(title = "Pharma Co-Authoring AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/demo")
def demo():
    return run_demo_pipeline()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/stream-demo")
async def stream_demo(request:Request):

    async def event_generator():

        async for event in run_demo_pipeline_stream():

            if await request.is_disconnected():
                break

            yield f"data: {json.dumps(event)}\n\n"

    
    return StreamingResponse(event_generator(), media_type="text/event-stream")