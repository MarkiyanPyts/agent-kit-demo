from agents import ItemHelpers, Runner
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from local_agents.orchestrator_agent import energy_company_data_manager_agent
from fastapi.responses import StreamingResponse
import asyncio
import json
from typing import Any, Optional

load_dotenv()

app = FastAPI()

class MessageToAgent(BaseModel):
    text: str

@app.post("/message")
async def message(message: MessageToAgent):
    async def event_stream():
        print("hit endpoint:")
        result = Runner.run_streamed(energy_company_data_manager_agent, message.text)

        try:
            # Optional: send a "hello" event so clients know the stream is alive
            yield "event: hello\ndata: {}\n\n"

            async for event in result.stream_events():
                # Ignore raw deltas
                if event.type == "raw_response_event":
                    continue

                elif event.type == "agent_updated_stream_event":
                    payload = {"agent_name": event.new_agent.name}
                    print(f"Agent updated: {event.new_agent.name}")
                    yield f"event: agent_update\ndata: {json.dumps(payload)}\n\n"

                elif event.type == "run_item_stream_event":
                    it = event.item
                    if it.type == "tool_call_item":
                        print("-- Tool was called")
                        yield f"event: tool_call\ndata: {json.dumps({'status': 'called'})}\n\n"

                    elif it.type == "tool_call_output_item":
                        print(f"-- Tool output: {it.output}")
                        yield f"event: tool_output\ndata: {json.dumps({'output': it.output})}\n\n"

                    elif it.type == "message_output_item":
                        text = ItemHelpers.text_message_output(it)
                        print(f"-- Message output:\n{text}")
                        yield f"event: message\ndata: {json.dumps({'text': text})}\n\n"

                    else:
                        # Unknown item type; you can choose to ignore or log
                        yield f"event: debug\ndata: {json.dumps({'item_type': it.type})}\n\n"

                # ignore other event types by default

        finally:
            # If the stream object supports async close, close it
            aclose = getattr(result, "aclose", None)
            if aclose and asyncio.iscoroutinefunction(aclose):
                await aclose()

            # Signal completion to the client
            yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        event_stream(),  # <-- now an async generator (async iterable), not a bare coroutine
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@app.get("/")
def root():
    return {"message": "Welcome to agents API!"}
