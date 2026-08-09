"""
Tests for Gem Trinity Genesis API
Run with: pytest tests/test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add local-watcher to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'local-watcher'))

from api_server import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints."""
    
    def test_root_returns_online(self):
        """Root endpoint should return online status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "Gem Trinity Genesis" in data["message"]
    
    def test_api_status_returns_system_info(self):
        """Status endpoint should return system health."""
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert "system" in data
        assert "integrity" in data
        assert data["system"] == "online"


class TestMetricsEndpoints:
    """Test metrics and transparency endpoints."""
    
    def test_metrics_returns_percentages(self):
        """Metrics endpoint should return determinism vs LLM percentages."""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_operations" in data
        assert "determinism_percentage" in data
        assert "llm_percentage" in data
        assert "philosophy" in data
        # Percentages should be valid
        assert 0 <= data["determinism_percentage"] <= 100
        assert 0 <= data["llm_percentage"] <= 100
    
    def test_metrics_dashboard_returns_ascii(self):
        """Dashboard endpoint should return ASCII visualization."""
        response = client.get("/api/metrics/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "ascii_dashboard" in data
        assert "metrics" in data


class TestArchitectEndpoints:
    """Test Architect agent endpoints."""
    
    def test_architect_history_returns_list(self):
        """History endpoint should return list of payloads."""
        response = client.get("/api/architect/history")
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert isinstance(data["history"], list)
    
    def test_architect_generate_requires_fields(self):
        """Generate should validate required fields."""
        response = client.post("/api/architect/generate", json={})
        # Should fail validation
        assert response.status_code == 422
    
    def test_architect_generate_with_valid_data(self):
        """Generate should create payload with valid input."""
        response = client.post("/api/architect/generate", json={
            "use_case": "Test automation project",
            "domain": "custom",
            "complexity": "simple",
            "model": "gemini-2.0"
        })
        assert response.status_code == 200
        data = response.json()
        assert "payload_id" in data
        assert "prd" in data
        assert "spec_contract" in data


class TestBuilderEndpoints:
    """Test Builder agent endpoints."""
    
    def test_builder_agents_returns_list(self):
        """Agents endpoint should return list."""
        response = client.get("/api/builder/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert isinstance(data["agents"], list)
    
    def test_builder_queue_returns_status(self):
        """Queue endpoint should return build queue."""
        response = client.get("/api/builder/queue")
        assert response.status_code == 200
        data = response.json()
        assert "queue" in data


class TestSkillsEndpoints:
    """Test Skills orchestration endpoints."""
    
    def test_skills_available_returns_list(self):
        """Available skills endpoint should return list."""
        response = client.get("/api/skills/available")
        assert response.status_code == 200
        data = response.json()
        assert "skills" in data
        assert isinstance(data["skills"], list)
    
    def test_skills_orchestrate_with_context(self):
        """Orchestrate should return skills based on context."""
        response = client.post("/api/skills/orchestrate", json={
            "domain": "sap",
            "complexity": "medium",
            "useCase": "Automate monthly close",
            "objectives": ["validation", "reporting"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "skills" in data
        assert "mcps" in data
        assert data["processing_type"] == "deterministic"


class TestProjectsEndpoints:
    """Test Projects management endpoints."""
    
    def test_projects_returns_list(self):
        """Projects endpoint should return all projects."""
        response = client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert isinstance(data["projects"], list)


class TestSAPEndpoints:
    """Test SAP simulator endpoints."""
    
    def test_sap_use_cases_returns_list(self):
        """SAP use cases should return predefined cases."""
        response = client.get("/api/sap/use_cases")
        assert response.status_code == 200
        data = response.json()
        assert "use_cases" in data


class TestRateLimiting:
    """Test rate limiting protection."""
    
    def test_rapid_requests_allowed_within_limit(self):
        """Multiple rapid requests within limit should succeed."""
        for _ in range(10):
            response = client.get("/api/status")
            assert response.status_code == 200


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
