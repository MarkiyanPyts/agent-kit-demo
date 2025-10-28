from agents import ItemHelpers, Runner, trace, RunItemStreamEvent
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from local_agents.orchestrator_agent import energy_company_data_manager_agent
from openai.types.responses import ResponseTextDeltaEvent
from fastapi.responses import StreamingResponse
import asyncio
import json
from openai import OpenAI

load_dotenv()

app = FastAPI()

class MessageToAgent(BaseModel):
    text: str

tool_item_types=set()
@app.post("/message")
async def message(message: MessageToAgent):
    async def event_stream():
        print("hit endpoint:")
        with trace(workflow_name="agentic_demo"):
            result = Runner.run_streamed(energy_company_data_manager_agent, message.text)
            tool_names_map = {}
            try:
                # Optional: send an initial event to keep the connection alive
                yield "event: hello\ndata: {}\n\n"

                
                current_agent_name="unknown_agent"
                async for event in result.stream_events():
                    

                    if (hasattr(event, "new_agent")): 
                        current_agent_name = getattr(event.new_agent, "name", "unknown_agent")
                    if (hasattr(event, "item")): 
                        current_agent_name = getattr(event.item.agent, "name", "unknown_agent")


                    # 1️⃣ Stream raw token deltas (console + SSE)
                    if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                        if (hasattr(event, "data") and hasattr(event.data, "delta")):
                            print(event.data.delta, end="", flush=True)
                            yield f"event: delta\ndata: {json.dumps({'agent_name': current_agent_name, 'delta': event.data.delta})}\n\n"
                        continue

                    # 2️⃣ Agent lifecycle updates
                    elif event.type == "agent_updated_stream_event":
                        current_agent_name = event.new_agent.name
                        print(f"Agent updated: {current_agent_name}")
                        yield f"event: agent_update\ndata: {json.dumps({'agent_name': current_agent_name})}\n\n"

                    # 3️⃣ Run item events
                    elif event.type == "run_item_stream_event":
                        it = event.item
                        # Tool call started
                        tool_item_types.add(it.type)
                        print(tool_item_types)
                        if it.type == "tool_call_item":
                            
                            raw_args = it.raw_item.arguments
                            tool_call_arguments = ''
                            # Normalize arguments so they’re JSON-safe
                            try:
                                tool_call_arguments = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                            except Exception:
                                tool_call_arguments = str(raw_args)
                            # breakpoint()
                            call_id=getattr(it.raw_item, "call_id", "")
                            tool_name = getattr(it.raw_item, "name", "unknown_tool")
                            tool_names_map[call_id] = tool_name
                            print(f"-- Agent {current_agent_name} called tool: {tool_name} with arguments: {tool_call_arguments} call_id: {call_id}")
                            yield f"event: tool_call\ndata: {json.dumps({'call_id': call_id, 'agent_name': current_agent_name, 'tool_name': tool_name, 'status': 'called', 'arguments': tool_call_arguments})}\n\n"


                        # Tool produced output
                        elif it.type == "tool_call_output_item":
                            call_id=it.raw_item.get("call_id", "")
                            # breakpoint()
                            tool_name = getattr(it.raw_item, "name", tool_names_map[call_id])
                            print(f"-- Agent {current_agent_name} received output from {tool_name}: {it.output}; call_id: {call_id}")
                            yield f"event: tool_output\ndata: {json.dumps({'call_id': call_id, 'agent_name': current_agent_name, 'tool_name': tool_name, 'output': it.output})}\n\n"

                        # Regular message output
                        elif it.type == "message_output_item":
                            text = ItemHelpers.text_message_output(it)
                            print(f"-- Agent {current_agent_name} message output:\n{text}")
                            yield f"event: message\ndata: {json.dumps({'agent_name': current_agent_name, 'text': text})}\n\n"

                        # Fallback for unknown event types
                        else:
                            yield f"event: debug\ndata: {json.dumps({'agent_name': current_agent_name, 'item_type': it.type})}\n\n"

            finally:
                # Properly close stream if supported
                aclose = getattr(result, "aclose", None)
                if aclose and asyncio.iscoroutinefunction(aclose):
                    await aclose()

                # Signal completion to the client
                yield f"event: done\ndata: {json.dumps({'agent_name': current_agent_name})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@app.post("/justllm")
async def justllm(message: MessageToAgent):

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-5-nano",
        reasoning_effort="low",
        messages=[
            {"role": "user", "content": f"translate the following text to english, this is annotation on work order for oil and gas company: {message.text}"}
        ]
    )
    return {"response": response.choices[0].message.content}

@app.get("/")
def root():
    return {"message": "Welcome to agents API!"}
