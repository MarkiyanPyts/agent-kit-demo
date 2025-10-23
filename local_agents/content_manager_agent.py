from agents import Agent, ModelSettings
from openai.types.shared.reasoning import Reasoning

from pydantic import BaseModel, Field
from typing import Optional


from local_agents.markdown_table_generator_agent import markdown_table_generator_agent
markdown_table_generator_agent_tool = markdown_table_generator_agent.as_tool(tool_name="Markdown_Table_Creator_Tool", tool_description="tool for creating markdown tables" )


content_manager_instructions = """
You are a content manager of energy company, create clear and concice responses

If input data contains data that can be represented as a table use Markdown_Table_Creator_Tool.
You should newer generate table yourself"""

content_manager_agent = Agent(
    name="Energy_Company_Content_Manager",
    instructions=content_manager_instructions,
    tools=[markdown_table_generator_agent_tool],
    model="gpt-5-mini",
    model_settings=ModelSettings(
        # store=True,
        reasoning=Reasoning(
            effort="low",
            summary="auto"
        )
    )
)