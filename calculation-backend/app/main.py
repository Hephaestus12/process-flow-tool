from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Flowchart API",
    description="API for managing flowcharts using DynamoDB as the backend",
    version="1.0.0",
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
