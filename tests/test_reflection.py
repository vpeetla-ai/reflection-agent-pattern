from reflection_agent_pattern import ReflectionAgent, ScriptedCritic, ScriptedGenerator


def test_reflection_revises_until_quality_gate_passes() -> None:
    result = ReflectionAgent(ScriptedGenerator(), ScriptedCritic()).run("Generate code")

    assert len(result.attempts) == 2
    assert result.attempts[-1].critique.approved
    assert "validation details" in result.answer

