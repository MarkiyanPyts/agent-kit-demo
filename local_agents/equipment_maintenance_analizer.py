import asyncio
from agents import Agent, function_tool, Runner
from typing import List, Optional, Annotated
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

import csv
import os

csv_content = []

# Get directory where this Python file is located
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "../data/Equipment_Maintenance_Logs_&_Predictive_Failure_Signals.csv")

with open(file_path, newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        csv_content.append(row)

@function_tool
def getEquipmentMeintenanceLogs():
    """Provides Equipment Maintenance Logs"""
    print('Getting maintainance logs:')
    return csv_content


class MaintenanceLogItem(BaseModel):
    log_id: str = Field(description="Log_ID")
    project_id: str = Field(description="Project_ID")
    equipment_type: str = Field(description="Equipment_Type")
    equipment_id: str = Field(description="Equipment_ID")
    installation_date: str = Field(description="Installation_Date")
    last_maintenance_date: str = Field(description="Last_Maintenance_Date")
    next_scheduled_maintenance_date: str = Field(description="Next_Scheduled_Maintenance_Date")
    runtime_hours: Annotated[float, Field(ge=0, description="Runtime_Hours")]  # non-negative
    failure_risk_score: Annotated[float, Field(ge=0, le=1, description="Failure_Risk_Score")]  # between 0 and 1
    sensors_anomaly_count: Annotated[int, Field(ge=0, description="Sensors_Anomaly_Count")]  # non-negative integer
    maintenance_type: str = Field(description="Maintenance_Type")
    outcome: str = Field(description="Outcome")
    notes: Optional[str] = Field(None, description="Notes")

class EquipmentMaintenanceAnalyzerOutputSchema(BaseModel):
    logs: List[MaintenanceLogItem] = Field(description="Logs")
    


# Create orchestrator with conditional tools
equipment_maintenance_analizer_agent = Agent(
    name="equipment_maintenance_analizer_agent",
    model="gpt-5-mini",
    instructions=(
        """
            You are an advanced AI Maintenance Analyst specializing in renewable and conventional energy infrastructure. You analyze structured maintenance logs for various equipment used in global energy projects, including wind, solar, gas, and oil systems.

            Each record in your dataset contains information about equipment type, runtime hours, failure risk scores, maintenance schedules, sensor anomalies, and outcomes.

            Your objectives are to return logs relevant to customer request following strict output schema
        """
    ),
    tools=[getEquipmentMeintenanceLogs],
    output_type=EquipmentMaintenanceAnalyzerOutputSchema
)

# async def main():
#     result = await Runner.run(equipment_maintenance_analizer_agent, "Show me top 3 logs with biggest risk score?")
#     print(result.final_output)

# asyncio.run(main())