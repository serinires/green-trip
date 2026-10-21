"""calc_emission: 이동수단과 거리로 탄소 배출량을 계산하는 도구 (계획서 5.1).

LLM 에이전트와 F1·F5가 모두 이 함수를 부른다.
계산은 여기서만 하고, LLM은 결과 숫자를 인용만 한다.
"""

import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# 지역별 계수 파일. 해외(Climatiq)는 나중에 추가.
FACTOR_FILES = {
    "KR": DATA_DIR / "emission_factors.json",
}


class EmissionResult(BaseModel):
    mode: str
    distance_km: float
    region: str
    kgco2e: float
    factor_g_per_pkm: float  # 사용한 계수 (g CO2 / 인·km)
    factor_version: str  # 어떤 계수표를 썼는지 (리포트에 표시)


@lru_cache
def load_factors(region: str) -> dict:
    """계수 파일을 한 번만 읽고 메모리에 캐시한다."""
    path = FACTOR_FILES.get(region)
    if path is None:
        raise ValueError(
            f"지원하지 않는 지역: {region}. 가능한 지역: {sorted(FACTOR_FILES)}"
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def calc_emission(mode: str, distance_km: float, region: str = "KR") -> EmissionResult:
    """거리(km) × 계수(g/인km) / 1000 = kgCO2e"""
    if distance_km < 0:
        raise ValueError(f"거리는 0 이상이어야 합니다: {distance_km}")

    table = load_factors(region)
    factors = table["factors"]
    if mode not in factors:
        # 에러 메시지에 가능한 값을 넣어두면 LLM이 보고 다시 고를 수 있다 (계획서 5.5)
        raise ValueError(f"알 수 없는 이동수단: {mode}. 가능한 값: {sorted(factors)}")

    factor = factors[mode]
    kg = distance_km * factor / 1000

    return EmissionResult(
        mode=mode,
        distance_km=distance_km,
        region=region,
        kgco2e=round(kg, 4),
        factor_g_per_pkm=factor,
        factor_version=table["version"],
    )
