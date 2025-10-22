from agents import Agent, Runner
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from local_agents.orchestrator_agent import energy_company_data_manager_agent
from openai.types.responses import ResponseTextDeltaEvent
from fastapi.responses import StreamingResponse
import asyncio
from typing import Any, Optional
import json

load_dotenv()

app = FastAPI()

class MessageToAgent(BaseModel):
    text: str

RAW_TEXT_TYPES = {
    "raw_response_event",            # your runner's type
    "response.output_text.delta",    # OpenAI Responses stream type
}

TOOL_EVENT_TYPES = {
    "tool_call.started",
    "tool_call.delta",
    "tool_call.completed",
    "agent.tool.started",
    "agent.tool.delta",
    "agent.tool.completed",
    "response.tool_call.created",
    "response.tool_call.delta",
    "response.tool_call.completed",
}

def _sse(event: str, data: Any, *, id: Optional[str] = None) -> str:
    """
    Build a single SSE frame. Data is JSON-encoded unless it's already a str.
    """
    if not isinstance(data, str):
        data = json.dumps(data, ensure_ascii=False)
    # Split into lines to comply with SSE "data:" per line rule
    lines = [f"event: {event}"]
    if id is not None:
        lines.append(f"id: {id}")
    for line in str(data).splitlines() or [""]:
        lines.append(f"data: {line}")
    lines.append("")  # blank line terminates the SSE message
    return "\n".join(lines) + "\n"


event_types=set()

@app.post("/message")
async def message(message: "MessageToAgent"):
    async def event_stream():
        print('hit endpoint:')
        result = Runner.run_streamed(energy_company_data_manager_agent, message.text)

        try:
            async for event in result.stream_events():
                
                etype = getattr(event, "type", "")
                data = getattr(event, "data", None)
                event_types.add(etype)
                print(event_types)
                yield etype
                # 1) Raw text deltas as SSE "delta"
                # if etype in RAW_TEXT_TYPES or isinstance(data, ResponseTextDeltaEvent):
                #     delta = getattr(data, "delta", None)
                #     if delta:
                #         yield _sse("delta", delta)
                #     continue

                # 2) Tool/agent events as SSE "tool" with JSON payload
                if etype in TOOL_EVENT_TYPES:
                    payload = {
                        "type": etype,
                        "name": getattr(data, "name", None),
                        "id": getattr(data, "id", None),
                        "args": getattr(data, "args", None),
                        "args_delta": getattr(data, "delta", None),
                        "result": getattr(data, "result", None),
                        "created": getattr(data, "created", None),
                    }
                    yield _sse("tool", payload)
                    continue

                # ignore everything else

        finally:
            # close the underlying stream if supported
            aclose = getattr(result, "aclose", None)
            # breakpoint()
            if asyncio.iscoroutinefunction(aclose):
                await result.aclose()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # optional but often helpful:
            "X-Accel-Buffering": "no",
        },
    )

@app.get('/')
def root():
    return {"message": "Welcome to agents API!"}