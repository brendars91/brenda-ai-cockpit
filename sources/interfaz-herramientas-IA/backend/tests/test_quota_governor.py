from datetime import UTC, datetime, timedelta

from cockpit_core.quota_governor import ProviderPolicy, QuotaGovernor, QuotaPolicy


class Clock:
    def __init__(self) -> None:
        self.now = datetime(2026, 6, 7, 10, 0, tzinfo=UTC)

    def advance(self, delta: timedelta) -> None:
        self.now += delta


def policy() -> QuotaPolicy:
    p = ProviderPolicy(rolling_5h_budget=100, weekly_budget=300, warning_threshold=0.2)
    return QuotaPolicy(zai=p, chatgpt=p, claude=p)


def test_quota_allows_when_budget_available() -> None:
    clock = Clock()
    governor = QuotaGovernor(policy(), now=lambda: clock.now)

    decision = governor.check(provider="zai", estimated_units=10, task_value="normal")

    assert decision.kind == "allow"


def test_quota_defers_low_value_work_near_threshold() -> None:
    clock = Clock()
    governor = QuotaGovernor(policy(), now=lambda: clock.now)
    governor.record_consumption(provider="zai", units=85, source="test")

    decision = governor.check(provider="zai", estimated_units=5, task_value="low")

    assert decision.kind == "defer"
    assert decision.retry_after is not None


def test_quota_degrades_normal_work_to_alternative_provider() -> None:
    clock = Clock()
    governor = QuotaGovernor(policy(), now=lambda: clock.now)
    governor.record_consumption(provider="zai", units=85, source="test")

    decision = governor.check(
        provider="zai",
        estimated_units=5,
        task_value="normal",
        alternative_providers=["chatgpt"],
    )

    assert decision.kind == "degrade"
    assert decision.alternative_provider == "chatgpt"


def test_quota_freezes_when_budget_is_exceeded() -> None:
    clock = Clock()
    governor = QuotaGovernor(policy(), now=lambda: clock.now)

    governor.record_consumption(provider="zai", units=101, source="test")

    assert governor.is_frozen() is True
    decision = governor.check(provider="chatgpt", estimated_units=1, task_value="critical")

    assert decision.kind == "deny"


def test_rolling_window_resets_with_injected_clock() -> None:
    clock = Clock()
    governor = QuotaGovernor(policy(), now=lambda: clock.now)
    governor.record_consumption(provider="zai", units=90, source="test")

    clock.advance(timedelta(hours=5, seconds=1))

    assert governor.window(provider="zai", window_type="rolling_5h").consumed == 0
