import os
import json
import time
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv

load_dotenv()

# ——————————————
# 1. Setup
# ——————————————
PROJECT_ENDPOINT = os.environ["PROJECT_ENDPOINT"]
DATA_AGENT_ID    = os.environ["DATA_INGEST_AGENT_ID"]
NEWS_AGENT_ID    = os.environ["NEWS_AGENT_ID"]
RISK_AGENT_ID    = os.environ["RISK_MODEL_AGENT_ID"]

client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential()
)

# ——————————————
# 2. Ingest CSV
# ——————————————
ingest_thread = client.agents.threads.create(agent_id=DATA_AGENT_ID)
ingest_prompt = (
    "Ingest the chip SCRM dataset located at "
    "`/backend/data/realistic_chip_scrm_dataset_100rows.csv` and return a JSON array of objects with exactly these fields:\n"
    "- productId (string)\n"
    "- chipType (string)\n"
    "- node (string)\n"
    "- partNumber (string)\n"
    "- unitPrice (number)\n"
    "- supplierLocation (string)\n"
    "- wipInventory (integer)\n"
    "- safetyStockLevel (integer)\n"
    "- supplierRiskScore (string)\n"
    "- countryRiskLevel (string)\n"
    "- leadTimeRisk (string)"
)
client.agents.messages.create(
    thread_id=ingest_thread.id,
    role="user",
    content=ingest_prompt
)

# simple wait; in production poll for new messages instead
time.sleep(5)

ingest_msgs   = list(client.agents.messages.list(thread_id=ingest_thread.id))
raw_shipments = ingest_msgs[-1].content
shipments     = json.loads(raw_shipments)

print("🚚 Ingested Shipments:")
print(json.dumps(shipments, indent=2))


# ——————————————
# 3. Enrich with News Risk
# ——————————————
news_thread = client.agents.threads.create(agent_id=NEWS_AGENT_ID)

# Build queries per supplierLocation
queries = [
    f"{pkg['supplierLocation']} shipping conflict news last 7 days"
    for pkg in shipments
]
news_payload = {"queries": queries}

client.agents.messages.create(
    thread_id=news_thread.id,
    role="user",
    content=json.dumps(news_payload)
)

time.sleep(5)

news_msgs     = list(client.agents.messages.list(thread_id=news_thread.id))
news_insights = json.loads(news_msgs[-1].content)

# Merge riskArticleCount into each shipment
for pkg, insight in zip(shipments, news_insights):
    pkg["riskArticleCount"] = insight.get("riskCount", 0)

print("\n📰 Shipments with News Risk:")
print(json.dumps(shipments, indent=2))


# ——————————————
# 4. Compute Risk Scores & CIs
# ——————————————
risk_thread = client.agents.threads.create(agent_id=RISK_AGENT_ID)

risk_request = {
    "query": "Compute overall risk score and 95% confidence interval for each shipment",
    "shipments": shipments
}

client.agents.messages.create(
    thread_id=risk_thread.id,
    role="user",
    content=json.dumps(risk_request)
)

time.sleep(5)

risk_msgs   = list(client.agents.messages.list(thread_id=risk_thread.id))
final_output = json.loads(risk_msgs[-1].content)

print("\n📊 Risk Modeling Results:")
print(json.dumps(final_output, indent=2))
