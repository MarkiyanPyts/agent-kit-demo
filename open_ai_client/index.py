from openai import AsyncAzureOpenAI
from agents import OpenAIChatCompletionsModel
import os
from dotenv import load_dotenv
load_dotenv()

openai_client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT")
)

azure_ai_foundry_model=OpenAIChatCompletionsModel(
    model="gpt-4.1", # This will use the deployment specified in your Azure OpenAI/APIM client
    openai_client=openai_client
)