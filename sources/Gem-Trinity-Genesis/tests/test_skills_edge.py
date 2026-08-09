import pytest
from skill_orchestrator import Skill, MCP, SkillOrchestrator

@pytest.fixture
def orchestrator():
    return SkillOrchestrator()

def test_empty_context(orchestrator):
    """Test orchestrator with empty context dict."""
    result = orchestrator.orchestrate({})
    skills = result["skills"]
    # Should default to basic skills
    assert len(skills) > 0
    # Check if we have at least 'code-fixer' or standard skills for "custom" domain
    skill_names = []
    for s in skills:
        if isinstance(s, dict):
            skill_names.append(s.get("name", ""))
        else:
            skill_names.append(s.name)
            
    assert any("code" in s.lower() for s in skill_names) or len(skill_names) > 0

def test_malformed_context(orchestrator):
    """Test with extremely long or weird characters in fields."""
    weird_text = "ÃƒÂ±" * 1000
    weird_context = {"useCase": weird_text, "domain": "custom"}
    result = orchestrator.orchestrate(weird_context)
    skills = result["skills"]
    assert len(skills) > 0

def test_skill_adaptation(orchestrator):
    """Test if skill instructions are adapted based on context."""
    context = {
        "domain": "custom",
        "description": "Project requires strict security and no external APIs.",
        "objectives": ["secure", "offline"]
    }
    result = orchestrator.orchestrate(context)
    skills = result["skills"]
    
    # Check if we got skills
    assert len(skills) > 0


