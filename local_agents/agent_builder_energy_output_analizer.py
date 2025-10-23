from agents import FileSearchTool, RunContextWrapper, Agent, ModelSettings, TResponseInputItem, Runner, RunConfig, trace
from pydantic import BaseModel
from openai.types.shared.reasoning import Reasoning

# Tool definitions
file_search = FileSearchTool(
  vector_store_ids=[
    "vs_68f610b630388191816350b7e3048343"
  ]
)
class EnergyProjectAnaliserSchema__ProjectsItem(BaseModel):
  Project_ID: str
  Site_Name: str
  Country: str
  Capacity_MW: str
  Annual_Output_GWh: str
  Status: str
  Ownership_percent: str
  Year_Commissioned: str
  CO2_Intensity_kg_per_MWh: str
  Notes: str


class EnergyProjectAnaliserSchema(BaseModel):
  Projects: list[EnergyProjectAnaliserSchema__ProjectsItem]


class EnergyProjectAnaliserContext:
  def __init__(self, workflow_input_as_text: str):
    self.workflow_input_as_text = workflow_input_as_text

def energy_project_analiser_instructions(run_context: RunContextWrapper[EnergyProjectAnaliserContext], _agent: Agent[EnergyProjectAnaliserContext]):
  workflow_input_as_text = run_context.context.workflow_input_as_text
  return f"""You are an expert on energy output readings for gas, oil and other sites

based on input text choose the best site that fits criteria"""
energy_project_analiser = Agent(
  name="Energy Project Analiser",
  instructions="""
    You are an expert on energy output readings for gas, oil and other sites
    based on input text choose the best site that fits criteria""",
  model="gpt-5-mini",
  tools=[
    file_search
  ],
  output_type=EnergyProjectAnaliserSchema,
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="low",
      summary="auto"
    )
  )
)


class WorkflowInput(BaseModel):
  input_as_text: str


# Main code entrypoint
async def run_workflow(workflow_input: WorkflowInput):
  with trace("Energy_Output_Analyzer"):
    state = {

    }
    workflow = workflow_input.model_dump()
    conversation_history: list[TResponseInputItem] = [
      {
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": workflow["input_as_text"]
          }
        ]
      }
    ]
    energy_project_analiser_result_temp = await Runner.run(
      energy_project_analiser,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_68f6056649bc819089da2c161d74deb9004026c8b634efb6"
      }),
      context=EnergyProjectAnaliserContext(workflow_input_as_text=workflow["input_as_text"])
    )

    conversation_history.extend([item.to_input_item() for item in energy_project_analiser_result_temp.new_items])

    energy_project_analiser_result = {
      "output_text": energy_project_analiser_result_temp.final_output.json(),
      "output_parsed": energy_project_analiser_result_temp.final_output.model_dump()
    }

    return energy_project_analiser_result


