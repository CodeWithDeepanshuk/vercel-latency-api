from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# upload q-vercel-latency.json into repo root
DATA_FILE = "q-vercel-latency.json"

class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: int

@app.post("/api/latency")
def latency(req: RequestBody):

    df = pd.read_json(DATA_FILE)

    df = df[df["region"].isin(req.regions)]

    result = {}

    for region in req.regions:

        temp = df[df["region"] == region]

        if len(temp) == 0:
            continue

        result[region] = {
            "avg_latency": float(temp["latency_ms"].mean()),
            "p95_latency": float(np.percentile(temp["latency_ms"],95)),
            "avg_uptime": float(temp["uptime"].mean()),
            "breaches": int((temp["latency_ms"] > req.threshold_ms).sum())
        }

    return result
