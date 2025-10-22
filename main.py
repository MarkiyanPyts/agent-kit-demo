from agents import Agent, Runner
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from local_agents.orchestrator_agent import energy_company_data_manager_agent
from openai.types.responses import ResponseTextDeltaEvent

load_dotenv()

api = FastAPI()

class MessageToAgent(BaseModel):
    text: str

@api.post('message')
async def message(message: MessageToAgent):
    print(message)
    result = Runner.run_streamed(energy_company_data_manager_agent, message.text)
    async for event in result.stream_events():
        print(f"event.type: {event.type}")
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)

@api.get('/')
def root():
    return {"message": "Welcome to agents API!"}