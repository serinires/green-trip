from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.tools.emission import EmissionResult, calc_emission

app = FastAPI(title="GREEN TRIP API")


@app.get("/health")
def health():
    """서버가 살아 있는지 확인용."""
    return {"status": "ok"}


class EmissionRequest(BaseModel):
    mode: str
    distance_km: float
    region: str = "KR"


# 개발·테스트용 엔드포인트. 계획서 7.3에는 없고,
# 나중에 /api/routes/compare (F1)가 이 함수를 내부에서 부른다.
@app.post("/api/tools/calc_emission", response_model=EmissionResult)
def calc_emission_api(req: EmissionRequest):
    try:
        return calc_emission(req.mode, req.distance_km, req.region)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
