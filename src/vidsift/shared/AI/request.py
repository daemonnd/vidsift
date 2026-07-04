from pydantic import BaseModel


class Request(BaseModel):
    user_prompt: str
    termperature: float = 0.7
    system_prompt: str = "You are a helpful assistant."
    max_tokens: int = 2000
    stream: bool = False

