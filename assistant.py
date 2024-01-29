from typing import List, Literal, Union

import httpx
from pydantic import BaseModel, Field

# constant
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "openhermes"
BUFFER_SIZE = 10
SYSTEM_MESSAGE = "You are multilingual expert writer that focuses on helping translate and correct text."
MULTI_SHOT_EXAMPLES = [
    "TRANSLATION: 'You excel at translating text from French to English' translates to 'Vous excellez à traduire des textes du français vers l'anglais.'",
    "TRANSLATION: 'Vous êtes le meilleur pour traduire de l'anglais vers le français.' translates to 'You are the best at translating from english to french'",
]
PROMPT_FORMATTING_CHARS = ""


# schemas
class Message(BaseModel):
    role: Union[Literal["system"], Literal["user"], Literal["assistant"]]
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: bool = Field(default=False)


# message buffer
class MessageBuffer(BaseModel):
    system_message: Message
    messages: List[Message] = Field(default_factory=list)
    buffer_size: int

    def add_message(self, message: Message):
        self.messages.append(message)

    def get_buffered_history(self) -> List[Message]:
        messages = [self.system_message]
        messages.extend(self.messages[-self.buffer_size :])

        return messages


# generation function
def chat_completion(ollama_api_base: str, request: ChatRequest) -> Message:
    ollama_api_base.rstrip() if ollama_api_base[-1] == "/" else ...
    request_url = ollama_api_base + "/api/chat"
    request_data = request.model_dump()
    response = httpx.post(request_url, json=request_data, timeout=None)

    raw_message = None
    try:
        raw_message = response.json()["message"]
    except Exception as e:
        print(f"Error extracting message. Did you pass the right model name?: {e}")

    message = Message(**raw_message)

    return message


if __name__ == "__main__":
    system_message = Message(
        role="system",
        content=SYSTEM_MESSAGE,
    )
    history_buffer = MessageBuffer(
        buffer_size=BUFFER_SIZE, system_message=system_message
    )
    for example in MULTI_SHOT_EXAMPLES:
        history_buffer.add_message(Message(role="assistant", content=example))

    print("Send a message, or type 'exit' to quit")
    while True:
        user_message = input("user: ")

        if user_message == "exit":
            exit()

        history_buffer.add_message(Message(role="user", content=user_message))
        messages = history_buffer.get_buffered_history()
        request = ChatRequest(model=OLLAMA_MODEL, messages=messages)

        assistant_message = chat_completion(OLLAMA_BASE_URL, request=request)
        print("assistant: ", assistant_message.content)

        history_buffer.add_message(assistant_message)
