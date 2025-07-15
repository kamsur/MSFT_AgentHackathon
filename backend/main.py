from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# Allow CORS (for frontend use, optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dummy data
supplychains = [
    {
        "id": "chip-supply-1",
        "title": "Chip Procurement – Asia to Europe"
    }
]

supplychain_details = {
    "chip-supply-1": {
        "id": "chip-supply-1",
        "title": "Chip Procurement – Asia to Europe",
        "totalRisk": 0.73,
        "riskLevel": "High",
        "lastUpdated": datetime(2025, 7, 15, 10, 32, 0).isoformat() + "Z",
        "steps": [
            {
                "id": "step-1",
                "order": 1,
                "category": "Raw Materials",
                "title": "Copper Mining – Peru",
                "description": "Raw copper extracted by Company X.",
                "location": "Peru",
                "company": "MiningCorp SA",
                "riskScore": 0.4,
                "riskLevel": "Medium",
                "riskDescription": "Political instability reported near the mining region."
            },
            {
                "id": "step-2",
                "order": 2,
                "category": "Transport",
                "title": "Shipment to Taiwan",
                "description": "Transported via Pacific route to TSMC",
                "location": "Pacific Ocean Route",
                "company": "GlobalShipping Ltd.",
                "riskScore": 0.9,
                "riskLevel": "High",
                "riskDescription": "Major strike at Port of Kaohsiung ongoing."
            }
        ]
    }
}

# GET /supplychains
@app.get("/supplychains")
def get_supplychains():
    return supplychains

# GET /supplychains/{id}
@app.get("/supplychains/{supplychain_id}")
def get_supplychain_detail(supplychain_id: str):
    if supplychain_id in supplychain_details:
        return supplychain_details[supplychain_id]
    raise HTTPException(status_code=404, detail="Supply chain not found")
