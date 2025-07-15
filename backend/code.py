import os
from dotenv import load_dotenv
import json

# Add references
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import ConnectedAgentTool, MessageRole, ListSortOrder, FileSearchTool, FilePurpose
from azure.identity import DefaultAzureCredential


# Clear the console
os.system('cls' if os.name=='nt' else 'clear')

# Load environment variables from .env file
load_dotenv()
project_endpoint = os.getenv("PROJECT_ENDPOINT")
model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

# Create the agents client

agents_client = AgentsClient(endpoint=project_endpoint, credential=DefaultAzureCredential())

# Agent instructions
orchestration_agent_name = "orchestrierungs_agent"
orchestration_instructions = """
You are the Orchestrator Agent in a multi-agent system for Supply Chain Risk Management.

## Goal
Coordinate specialist agents to analyze structured supply chain JSON data and produce domain-specific risk assessments.

## Behavior
- Receive the full supply chain JSON data.
- Call the SplitterAgent to split data into logical domains:
  - Raw Material Information
  - Logistics / Transportation Information
- For each domain, pass the domain data to the appropriate DomainRiskAgent.
- Collect all domain-specific risk assessments.
- Return a consolidated, well-structured final risk report.

## Important
- Always ensure data is correctly split by domain.
- Make sure all domain agents receive *only* their relevant data.
- Combine all results clearly and concisely.
"""

raw_material_agent_name = "raw_material_agent"
raw_material_agent_instructions = """
You are the Raw Material Risk Agent. Your task is to analyze Raw Material Information from the supply chain JSON data and identify potential supply chain risks.

## Consider:
- RawMaterialCountryOfOrigin: geopolitical or natural disaster risk
- RawMaterialCostPerUnit: cost volatility
- SupplierDependency: single-source or multi-source risks
- LeadTimeDays: potential for long lead times or variability

## Output
- Provide a clear risk analysis of raw materials sourcing.
- Highlight specific countries or suppliers with elevated risk.
- Suggest mitigation strategies such as diversification or stockpiling.
- Make your answer structured and easy to read.
"""

logistic_agent_name = "logistic_agent"
logistic_agent_instructions = """
You are the Logistics Risk Agent. Your task is to analyze the Logistics domain data for potential risks.
## Consider:
- AverageTransitTime
- ShippingMode
- OriginCountry risk
- ShippingCost variability
- Reliability

## Output
- Provide a clear risk assessment and recommendations to mitigate logistics risks.
"""

foundry_production_agent_name = 'foundry_production_agent'
foundry_production_agent_instructions = """
You are the Foundry Production Risk Agent. Your task is to analyze Foundry Production Data in the supply chain JSON and identify manufacturing risks.

## Consider:
- WaferLeadTimeDays: impact on production timelines
- WaferYield: production efficiency and risk of rework
- WaferCost: cost escalation risk
- FabCycleTimeDays: bottleneck potential

## Output
- Provide a clear risk assessment of production operations.
- Highlight lead time vulnerabilities, yield issues, or cost risks.
- Offer mitigation suggestions such as alternative foundries or improved forecasting.
- Make your analysis structured and easy to read.
"""

assembly_test_agent_name = 'assembly_test_agent'
assembly_test_agent_instructions = """
You are the Assembly & Test Risk Agent. Your task is to analyze Assembly & Test Data from the supply chain JSON and identify operational risks.

## Consider:
- AssemblyLeadTimeDays: delays in packaging and testing
- PackagingCostPerUnit: cost control risk
- AssemblyYield: yield losses
- TestPassRate: quality and reliability concerns

## Output
- Provide a clear risk assessment for the assembly and testing stages.
- Highlight any issues that could impact delivery or quality.
- Suggest mitigation strategies such as second-source OSATs or yield improvement programs.
- Make your analysis structured and easy to read.
"""

with agents_client:

    # Create the Booking Agent
    raw_material_agent = agents_client.create_agent(
        model=model_deployment,
        name=raw_material_agent_name,
        instructions=raw_material_agent_instructions
    )

    # Define the path to the file to be uploaded
    json_file_path = "realistic_chip_scrm_dataset_100rows.json"
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    text = json.dumps(data, indent=2)

    # Create the policy agent using the file search tool
    logistic_agent = agents_client.create_agent(
        model=model_deployment,
        name=logistic_agent_name,
        instructions=logistic_agent_instructions,
    )

    # Create the connected agent tools for all 3 agents
    # Note: The connected agent tools are used to connect the agents to the orchestrator agent
    raw_material_agent_tool = ConnectedAgentTool(
        id=raw_material_agent.id,
        name=raw_material_agent_name,
        description="Analyze the risk of given raw materials"
    )

    # add recherche_agent_tool
    logistic_agent_tool = ConnectedAgentTool(
        id=logistic_agent.id,
        name=logistic_agent_name,
        description="Analyze the risk of given logistic data."
    )

    # Create the Orchestrator Agent
    # This agent will coordinate the other agents based on user input
    orchestrator_agent = agents_client.create_agent(
                                                    model=model_deployment,
                                                    name=orchestration_agent_name,
                                                    instructions=orchestration_instructions,
                                                    tools=[
                                                        raw_material_agent_tool.definitions[0],
                                                        logistic_agent_tool.definitions[0]],
                                                    )
    thread = agents_client.threads.create()
    agents_client.messages.create(thread_id=thread.id, role=MessageRole.USER, content=text)

    

    print(f"Orchestrator-Agent '{orchestration_agent_name}' und verbundene Agenten wurden erfolgreich erstellt.")

    # === Thread for Terminal Interaction ===
    print("\nGib deine Reiseanfrage ein (oder 'exit' zum Beenden):")
    while True:
        user_input = 'Read the File and Split information into Raw Materials and Logistics. Discard the other information and send the data to resptive AI Agent for further analysis.'
        if user_input.strip().lower() == "exit":
            break

        agents_client.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=user_input,
        )

        print("Working in progress...")
        run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=orchestrator_agent.id)
        if run.status == "failed":
            print(f"Runtime Error: {run.last_error}")
            continue

        messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        for message in messages:
            if message.text_messages:
                last_msg = message.text_messages[-1]
                content = last_msg.text.value
                print(f"{message.role}:\n{last_msg.text.value}\n")
                with open('orchestrator_output.json', 'w', encoding='utf-8') as f:
                    json.dump({"role": message.role, "content": content}, f, indent=2)


    # Aufräumen
    # print("Lösche Agenten...")
    agents_client.delete_agent(orchestrator_agent.id)
    agents_client.delete_agent(raw_material_agent.id)
    agents_client.delete_agent(logistic_agent.id)
    print("All Answer Deleted.")
