from fastapi import FastAPI
import agent
import item

# Setup app
app = FastAPI()

# Add listener for message POST request
@app.post("/message/")
def create_item(item: item.Item):
    # Run AI Algorithm
    response_message = agent.chat(item)

    # Return output
    return {"message": response_message}