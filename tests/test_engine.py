import pytest
from engine.store import velocity
from engine.analyzer import classify, profile_specs

def test_velocity_calculation():
    prev = {"demo/repo": [1000, 50]}
    # Ref is older than 4 hours but within 48 hours
    now_ts = 1000 + (10 * 3600)
    current_stars = 150
    # 100 stars in 10 hours = 10 stars/hour * 24 = 240
    v = velocity("demo/repo", current_stars, prev, min_h=4, max_h=48, now_ts=now_ts)
    assert v == 240

def test_profile_specs():
    specs = profile_specs("A local-first LLM runner with CUDA support on RTX 3090", ["cuda", "sqlite"])
    assert specs["is_local_first"] is True
    assert specs["is_cuda_ready"] is True
    assert "24GB" in specs["hardware_req"]

from engine.analyzer import classify, profile_specs, generate_architectural_verdict

def test_classify():
    cat = classify("Fast LLM inference runner with GGUF quantization", ["llm", "gguf"])
    assert cat == "Local LLM Engines"

def test_generate_architectural_verdict():
    repo = {"name": "test-llm", "description": "Local LLM engine"}
    category = "Local LLM Engines"
    capabilities = {
        "hardware": {"floor": "24GB VRAM (CUDA)"},
        "deployment": ["local-only"],
        "integrations": ["mcp-server"],
        "intent_tags": ["gguf"]
    }
    health = {"stage": "experimental", "authenticity_score": 90}
    verdict, gotchas, comparison, replaces = generate_architectural_verdict(repo, category, capabilities, health)
    assert "Heavyweight architecture" in verdict
    assert "24GB+" in gotchas
    assert "Alternative to" in comparison
    assert isinstance(replaces, list)
    assert len(replaces) > 0

