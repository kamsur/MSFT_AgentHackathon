from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import subprocess
import os

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
        "id": "raw-materials",
        "title": "Raw Material related data for the supply chain"
    },
    {
        "id": "logistics",
        "title": "Logistics related data for the supply chain"
    }
]

supplychain_details = {
    "raw-materials": {
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

# POST /run-analysis
@app.post("/run-analysis")
def run_supply_chain_analysis():
    """Run the supply chain risk analysis using code.py"""
    try:
        # Change to the backend directory to run code.py
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Run code.py as a subprocess
        result = subprocess.run(
            ["python", "code.py"], 
            cwd=backend_dir,
            capture_output=True, 
            text=True, 
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            return {
                "status": "success",
                "message": "Supply chain analysis completed successfully",
                "output": result.stdout,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "message": "Analysis failed",
                "error": result.stderr,
                "output": result.stdout,
                "timestamp": datetime.now().isoformat()
            }
            
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Analysis timed out after 5 minutes",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to run analysis: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
