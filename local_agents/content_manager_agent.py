from agents import Agent
from pydantic import BaseModel, Field
from typing import Optional


from markdown_table_generator_agent import markdown_table_generator_agent
markdown_table_generator_agent_tool = markdown_table_generator_agent.as_tool(tool_name="Markdown_Table_Creator_Tool", tool_description="tool for creating markdown tables, to be used if input data can be represented as table" )


content_manager_instructions = """
You are a content manager of energy company, create clear and concice responses

If input data contains data that can be represented as a table use markdown_table_generator_agent_tool to format it into a nice table
"""

content_manager_agent = Agent(
    name="Energy_Company_Data_Manager",
    instructions=content_manager_instructions,
    tools=[markdown_table_generator_agent_tool],
    model="gpt-5-mini",
)