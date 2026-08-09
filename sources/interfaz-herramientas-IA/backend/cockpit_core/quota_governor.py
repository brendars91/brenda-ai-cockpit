from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal

ProviderName = Literal["zai", "chatgpt", "claude"]
TaskValue = Literal["low", "normal", "critical"]
DecisionKind = Literal["allow", "defer", "deny", "degrade"]
WindowType = Literal["rolling_5h", "weekly"]
PROVIDERS: tuple[ProviderName, ...] = ("zai", "chatgpt", "claude")


@dataclass(frozen=True)
class ProviderPolicy:
    rolling_5h_budget: int
    weekly_budget: int
    warning_threshold: float


@dataclass(frozen=True)
class QuotaPolicy:
    zai: ProviderPolicy
    chatgpt: ProviderPolicy
    claude: ProviderPolicy

    def provider(self, name: ProviderName) -> ProviderPolicy:
        if name == "zai":
            return self.zai
        if name == "chatgpt":
            return self.chatgpt
        return self.claude


@dataclass(frozen=True)
class QuotaDecision:
    provider: ProviderName
    kind: DecisionKind
    reason: str
    retry_after: datetime | None = None
    alternative_provider: ProviderName | None = None


@dataclass(frozen=True)
class WindowSnapshot:
    provider: ProviderName
    window_type: WindowType
    budget: int
    consumed: int
    remaining: int
    window_start: datetime
    window_end: datetime


@dataclass
class _Window:
    budget: int
    consumed: int
    window_start: datetime
    window_end: datetime


class QuotaGovernor:
    def __init__(self, policy: QuotaPolicy, *, now: Callable[[], datetime] | None = None) -> None:
        self._policy = policy
        self._now = now or (lambda: datetime.now(UTC))
        self._frozen = False
        self._freeze_reason: str | None = None
        current = self._now()
        self._windows: dict[ProviderName, dict[WindowType, _Window]] = {
            provider: {
                "rolling_5h": _Window(
                    budget=policy.provider(provider).rolling_5h_budget,
                    consumed=0,
                    window_start=current,
                    window_end=current + timedelta(hours=5),
                ),
                "weekly": _Window(
                    budget=policy.provider(provider).weekly_budget,
                    consumed=0,
                    window_start=current,
                    window_end=current + timedelta(days=7),
                ),
            }
            for provider in PROVIDERS
        }

    def check(
        self,
        *,
        provider: ProviderName,
        estimated_units: int,
        task_value: TaskValue,
        alternative_providers: list[ProviderName] | None = None,
    ) -> QuotaDecision:
        self._refresh_windows()
        if self._frozen:
            return QuotaDecision(
                provider=provider,
                kind="deny",
                reason=self._freeze_reason or "frozen",
            )

        limiting = self._most_constrained_window(provider)
        if estimated_units > limiting.remaining:
            return QuotaDecision(provider=provider, kind="deny", reason="insufficient quota")

        if self._near_threshold(provider):
            if task_value == "low":
                return QuotaDecision(
                    provider=provider,
                    kind="defer",
                    reason="provider near threshold",
                    retry_after=limiting.window_end,
                )
            if task_value == "normal":
                alt = self._find_alternative(estimated_units, alternative_providers or [])
                if alt is not None:
                    return QuotaDecision(
                        provider=provider,
                        kind="degrade",
                        reason="provider near threshold",
                        alternative_provider=alt,
                    )
        return QuotaDecision(provider=provider, kind="allow", reason="quota available")

    def record_consumption(self, *, provider: ProviderName, units: int, source: str) -> None:
        if source == "":
            raise ValueError("source is required")
        self._refresh_windows()
        for window in self._windows[provider].values():
            window.consumed += units
            if window.consumed > window.budget:
                self.freeze(f"{provider} quota exceeded")

    def window(self, *, provider: ProviderName, window_type: WindowType) -> WindowSnapshot:
        self._refresh_windows()
        window = self._windows[provider][window_type]
        return WindowSnapshot(
            provider=provider,
            window_type=window_type,
            budget=window.budget,
            consumed=window.consumed,
            remaining=window.budget - window.consumed,
            window_start=window.window_start,
            window_end=window.window_end,
        )

    def freeze(self, reason: str) -> None:
        self._frozen = True
        self._freeze_reason = reason

    def unfreeze(self) -> None:
        self._frozen = False
        self._freeze_reason = None

    def is_frozen(self) -> bool:
        return self._frozen

    def _refresh_windows(self) -> None:
        current = self._now()
        for provider_windows in self._windows.values():
            for window_type, window in provider_windows.items():
                if current >= window.window_end:
                    window.consumed = 0
                    window.window_start = current
                    window_duration = (
                        timedelta(hours=5) if window_type == "rolling_5h" else timedelta(days=7)
                    )
                    window.window_end = current + window_duration

    def _near_threshold(self, provider: ProviderName) -> bool:
        policy = self._policy.provider(provider)
        for window_type in ("rolling_5h", "weekly"):
            snapshot = self.window(provider=provider, window_type=window_type)
            remaining_ratio = snapshot.remaining / snapshot.budget
            if remaining_ratio <= policy.warning_threshold:
                return True
        return False

    def _most_constrained_window(self, provider: ProviderName) -> WindowSnapshot:
        rolling = self.window(provider=provider, window_type="rolling_5h")
        weekly = self.window(provider=provider, window_type="weekly")
        return rolling if rolling.remaining <= weekly.remaining else weekly

    def _find_alternative(
        self,
        units: int,
        alternatives: list[ProviderName],
    ) -> ProviderName | None:
        for alt in alternatives:
            decision = self.check(provider=alt, estimated_units=units, task_value="critical")
            if decision.kind == "allow":
                return alt
        return None
