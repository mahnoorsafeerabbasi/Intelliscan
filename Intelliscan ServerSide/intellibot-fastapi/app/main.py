# app/main.py
from fastapi import FastAPI
from app.api.endpoints import router
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as necessary for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router with a prefix
app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the IntelliScan API!"}

# Get port from environment variable, default to 8000
port = int(os.getenv("PORT", 4001))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4001)