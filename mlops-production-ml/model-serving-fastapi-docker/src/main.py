"""Minimal FastAPI model-serving skeleton.

Fill in `load_model` and the feature schema, then:
    uvicorn src.main:app --reload
"""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="model-serving-demo")

model = None  # TODO: load a real model, e.g. via mlflow.pyfunc.load_model(...)


class PredictRequest(BaseModel):
    # TODO: replace with real feature fields
    features: list[float]


class PredictResponse(BaseModel):
    prediction: float


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    # TODO: replace with model.predict([request.features])[0]
    prediction = sum(request.features)
    return PredictResponse(prediction=prediction)
