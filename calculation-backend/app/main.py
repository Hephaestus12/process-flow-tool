from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="Flowchart API",
    description="API for managing flowcharts",
    version="1.0.0",
)

# Configure CORS
origins = [
    "http://localhost:3000",  # your frontend URL
    "http://127.0.0.1:3000",    # if using 127.0.0.1
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or use ["*"] to allow all origins (not recommended in production)
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, reload=True)
