from fastapi import FastAPI
import agent
import item
from fastapi.middleware.cors import CORSMiddleware

# Setup app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add listener for message POST request
@app.post("/message/")
def create_item(item: item.Item):
    # Run AI Algorithm
    response_message = agent.chat(item)

    # Return output
    return {"message": response_message}