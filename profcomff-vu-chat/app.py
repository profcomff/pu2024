from datetime import datetime, timedelta
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="The simplest chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*', None],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

class Message(BaseModel):
    text: str
    author: str
    time: datetime | None = None

messages: list[Message] = []


@app.get('/message')
def get_message(start_from: datetime | None = None):
    now = datetime.utcnow()
    if start_from is None:
        start_from = now - timedelta(minutes=10)
    return {
        "messages": list(filter(lambda x: x.time >= start_from, messages)),
        "start_next_from": now,
    }


@app.post('/message')
def post_message(message: Message):
    message.time = datetime.utcnow()
    messages.append(message)
    return {'ok': True}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=80)
