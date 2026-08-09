from typing import assert_type

from cockpit_core.ports import AgentRuntimePort, GovernancePort, KnowledgePort, ModelProviderPort


def test_ports_are_importable_protocols() -> None:
    assert_type(AgentRuntimePort, type[AgentRuntimePort])
    assert_type(KnowledgePort, type[KnowledgePort])
    assert_type(GovernancePort, type[GovernancePort])
    assert_type(ModelProviderPort, type[ModelProviderPort])
