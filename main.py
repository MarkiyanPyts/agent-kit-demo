from agents import Agent, Runner
from dotenv import load_dotenv
from enum import IntEnum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from local_agents.agent_builder_energy_output_analizer import run_workflow as run_energy_output_analizer
from local_agents.agent_builder_energy_output_analizer import WorkflowInput
import asyncio

load_dotenv()



# api = FastAPI()

# agent = Agent(name="Assistant", instructions="You are a helpful assistant")

# result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
# print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.

async def run_agents():
    wi = WorkflowInput(input_as_text="what is best norway location in terms of energy efficiency")
    result = await run_energy_output_analizer(wi)
    print(result)

if __name__ == "__main__":
    asyncio.run(run_agents())