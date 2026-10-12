
from fastapi import FastAPI

app = FastAPI(
    title="NEXUS API",
    description="Enterprise AI platform API",
    version="0.1.0",
)


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "ok",
        "service": "nexus-api",
        "version": "0.1.0",
    }
