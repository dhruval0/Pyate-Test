from dotenv import load_dotenv
import os
import uvicorn

load_dotenv()

if __name__ == "__main__":
    uvicorn.run("server.api:app", host = "0.0.0.0", port = int(os.getenv("PORT",80)), lifespan="on")