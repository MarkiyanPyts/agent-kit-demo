from agents import Agent, handoff, ModelSettings, set_default_openai_client, add_trace_processor
# from local_agents.agent_builder_energy_output_analizer import energy_project_analiser
from local_agents.agent_builder_energy_output_analizer import WorkflowInput
from local_agents.equipment_maintenance_analizer import equipment_maintenance_analizer_agent
from local_agents.content_manager_agent import content_manager_agent
from openai.types.shared.reasoning import Reasoning
from open_ai_client.index import openai_client, azure_ai_foundry_model

set_default_openai_client(openai_client)

from agents.tracing.processors import ConsoleSpanExporter, BatchTraceProcessor
console_exporter = ConsoleSpanExporter()
console_processor = BatchTraceProcessor(exporter=console_exporter)
add_trace_processor(console_processor)

# energy_output_site_analizer_tool = energy_project_analiser.as_tool(tool_name="Sites_Energy_Output_Analizer", tool_description="""
#     Analizes Energy Output Per Site, returns only records relevant to user request, this is type of data that can be discovered in sites datasource:                                            
#     {
#     "Project_ID":"OUT013",
#     "Site_Name":"Norway Hydro Carbon Rich Field",
#     "Country":"Norway",
#     "Site_Type":"Oil",
#     "Capacity_MW":900,
#     "Annual_Output_GWh":5400,
#     "Ownership_%":55,
#     "Year_Commissioned":"2020",
#     "Status":"Operational",
#     "CO2_Intensity_kg_per_MWh":"290",
#     "Notes":"Hydro-carbon rich field Norway"
#     }
# """)

equipment_maintenance_analizer_agent_tool = equipment_maintenance_analizer_agent.as_tool(tool_name="Equipment_Maintenance_Logs_Analiser", tool_description="""
    Analizes equipment maintainance logs, returns only records relevant to user request
    
    here is example of a logs format available in data set
    {
    "Log_ID": "MAINT001",
    "Project_ID": "OUT003",
    "Equipment_Type": "Wind Turbine Rotor",
    "Equipment_ID": "WT-NCS-001",
    "Installation_Date": "2023-02-10",
    "Last_Maintenance_Date": "2025-06-15",
    "Next_Scheduled_Maintenance_Date": "2026-06-15",
    "Runtime_Hours": 12500,
    "Failure_Risk_Score": 0.18,
    "Sensors_Anomaly_Count": 2,
    "Maintenance_Type": "Preventive",
    "Outcome": "No issue",
    "Notes": "Offshore floating rotor inspected"
    }

""")


energy_company_data_manager_instructions = """
You are data manager of energy company data, you have the following tools:
- Equipment Maintenance Logs Analiser

user the appropriate tool then handoff to content_manager_agent for further processing,
newer reply yourself
"""


energy_company_data_manager_agent = Agent(
    name="Energy_Company_Data_Manager",
    instructions=energy_company_data_manager_instructions,
    tools=[
        # energy_output_site_analizer_tool,
        equipment_maintenance_analizer_agent_tool
    ],
    handoffs=[
        handoff(content_manager_agent)
    ],
    model=azure_ai_foundry_model,# was "gpt-5"
    model_settings=ModelSettings(
        store=True,
        # reasoning=Reasoning(
        #     effort="low",
        #     summary="auto"
        # )
    )
)