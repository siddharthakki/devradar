import pytest
from engine.store import velocity
from engine.analyzer import classify, profile_specs

def test_velocity_calculation():
    prev = {"demo/repo": [1000, 50]}
    # Ref is older than 4 hours but within 48 hours
    now_ts = 1000 + (10 * 3600)
    current_stars = 150
    # 100 stars in 10 hours = 10 stars/hour * 24 = 240
    v = velocity("demo/repo", current_stars, prev, min_h=4, max_h=48)
    assert v > 0

def test_profile_specs():
    specs = profile_specs("A local-first LLM runner with CUDA support on RTX 3090", ["cuda", "sqlite"])
    assert specs["is_local_first"] is True
    assert specs["is_cuda_ready"] is True
    assert "24GB" in specs["hardware_req"]
