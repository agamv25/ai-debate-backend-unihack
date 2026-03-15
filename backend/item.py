from pydantic import BaseModel

# Message list JSON fields
class Message(BaseModel):
    speaker: str
    message: str

# Main item JSON fields
class Item(BaseModel):
    topic: str
    speaker: str
    conversation: list[Message]