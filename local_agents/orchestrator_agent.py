from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
from agent_builder_energy_output_analizer import Agent as energy_output_analizer_agent
from agent_builder_energy_output_analizer import WorkflowInput

energy_output_site_analizer_tool = energy_output_analizer_agent.as_tool(tool_name="Evergy Output Analizer", tool_description="""
    Analize Energy Output Per Site, you can ask questions about energy plant sites this is type of data that can be discovered in sites datasource:                                            
    {
    "Project_ID":"OUT013",
    "Site_Name":"Norway Hydro Carbon Rich Field",
    "Country":"Norway",
    "Site_Type":"Oil",
    "Capacity_MW":900,
    "Annual_Output_GWh":5400,
    "Ownership_%":55,
    "Year_Commissioned":"2020",
    "Status":"Operational",
    "CO2_Intensity_kg_per_MWh":"290",
    "Notes":"Hydro-carbon rich field Norway"
    }
""")


orchestrator = "You are a sales manager working for ComplAI. You use the tools given to you to generate cold sales emails. \
You never generate sales emails yourself; you always use the tools. \
You try all 3 sales agent tools at least once before choosing the best one. \
You can use the tools multiple times if you're not satisfied with the results from the first try. \
You select the single best email using your own judgement of which email will be most effective. \
After picking the email, you handoff to the Email Manager agent to format and send the email."


sales_manager = Agent(
    name="Sales Manager",
    instructions=orchestrator,
    tools=tools,
    handoffs=handoffs,
    model="gpt-4o-mini")

message = "Send out a cold sales email addressed to Dear CEO from Alice"

with trace("Automated SDR"):
    result = await Runner.run(sales_manager, message)