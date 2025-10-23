import asyncio
from agents import Agent, Runner
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from agents import Agent, ModelSettings
from openai.types.shared.reasoning import Reasoning

load_dotenv()

class MarkdownGeneratorInputParams(BaseModel):
    input_text: str = Field(description="Input text query")


class MarkdownGeneratorToolOutputSchema(BaseModel):
    result: str = Field(description='Markdown table output, or explicit text telling that you can not generate table based on input content')
    parameters: MarkdownGeneratorInputParams = Field(description='Input request text')

markdown_table_generator_agent = Agent(
    name="markdown_table_generator_agent",
    model="gpt-5-mini",
    instructions=(
        """
            You are expert at creating markdown tables from data provided to you, here is example of table format expected

            | User ID | Name | Email | Created At |
            |---------|------|-------|------------|
            | 1 | John Doe | john@example.com | 2024-01-15 |
            | 2 | Jane Smith | jane@example.com | 2024-01-20 |
            | 3 | Bob Wilson | bob@example.com | 2024-02-01 |
            | 4 | Alice Brown | alice@example.com | 2024-02-10 |
            | 5 | Charlie Davis | charlie@example.com | 2024-02-15 |
        """
    ),
    output_type=MarkdownGeneratorToolOutputSchema,
    model_settings=ModelSettings(
        store=True,
        reasoning=Reasoning(
            effort="low",
            summary="auto"
        )
    )
)