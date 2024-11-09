from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

class InputPayload(BaseModel):
    message: str

class TrimmedResponse(BaseModel):
    id: str
    text: str

# def guardrail_call(message: str):
#     if "Write a review for an employee" not in message:
#         raise HTTPException(
#             status_code=400,
#             detail="The request must contain the phrase 'Write a review for an employee'."
#         )

@app.post("/feedback", response_model=TrimmedResponse)
async def process_response(payload: InputPayload):
    # guardrail_call(payload.message)

    try:
        llm_response = requests.post("https://cohere-node-production.up.railway.app/chat", json=payload.dict())
        llm_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

    response_data = llm_response.json()
    trimmed_data = {
        "id": response_data["id"],
        "text": response_data["message"]["content"][0]["text"]
    }

    return trimmed_data