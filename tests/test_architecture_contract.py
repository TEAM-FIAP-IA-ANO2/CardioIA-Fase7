from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_openai_agents_sdk_contract_is_present():
    source = (ROOT / "cardioia" / "agents_pipeline.py").read_text(encoding="utf-8")
    for token in ["from agents import Agent", "function_tool", "handoffs=[", "SQLiteSession", "output_type=FinalResponse", "Runner.run"]:
        assert token in source


def test_no_google_adk_dependency():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    assert "google-adk" not in requirements
    assert "openai-agents" in requirements
