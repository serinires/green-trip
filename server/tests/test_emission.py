import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.tools.emission import calc_emission


# ---- 함수 테스트 ----

def test_bus_10km():
    # 63 g/인km × 10km = 630g = 0.63kg
    r = calc_emission("bus", 10)
    assert r.kgco2e == pytest.approx(0.63)
    assert r.factor_g_per_pkm == 63


def test_car_is_more_than_subway():
    # 같은 거리면 승용차가 지하철보다 많아야 한다
    car = calc_emission("car", 5).kgco2e
    subway = calc_emission("subway", 5).kgco2e
    assert car > subway


def test_walk_is_zero():
    assert calc_emission("walk", 3).kgco2e == 0


def test_zero_distance():
    assert calc_emission("car", 0).kgco2e == 0


def test_unknown_mode_lists_valid_modes():
    with pytest.raises(ValueError) as e:
        calc_emission("rocket", 10)
    assert "bus" in str(e.value)  # 에러 메시지에 가능한 값이 들어 있어야 함


def test_negative_distance():
    with pytest.raises(ValueError):
        calc_emission("bus", -1)


def test_unsupported_region():
    with pytest.raises(ValueError):
        calc_emission("bus", 10, region="FR")


def test_result_has_factor_version():
    # 리포트에 계수 출처를 표시해야 하므로 버전이 꼭 있어야 함
    assert calc_emission("bus", 1).factor_version == "kr-gg-202401"


# ---- API 테스트 ----

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_api_calc_emission():
    res = client.post("/api/tools/calc_emission", json={"mode": "car", "distance_km": 10})
    assert res.status_code == 200
    assert res.json()["kgco2e"] == pytest.approx(1.48)


def test_api_bad_mode_returns_400():
    res = client.post("/api/tools/calc_emission", json={"mode": "rocket", "distance_km": 10})
    assert res.status_code == 400
