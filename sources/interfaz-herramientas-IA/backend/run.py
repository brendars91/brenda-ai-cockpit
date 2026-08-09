"""Run the Cockpit API server locally."""
from __future__ import annotations

import pathlib

import uvicorn

from cockpit_core.context_fabric import EventLog
from cockpit_core.quota_governor import (
    ProviderPolicy,
    QuotaGovernor,
    QuotaPolicy,
)
from cockpit_web.app import create_app


def main() -> None:
    db_path = pathlib.Path(__file__).parent / "data" / "events.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    event_log = EventLog(db_path)
    policy = QuotaPolicy(
        zai=ProviderPolicy(
            rolling_5h_budget=100,
            weekly_budget=1000,
            warning_threshold=0.2,
        ),
        chatgpt=ProviderPolicy(
            rolling_5h_budget=200,
            weekly_budget=2000,
            warning_threshold=0.2,
        ),
        claude=ProviderPolicy(
            rolling_5h_budget=150,
            weekly_budget=1500,
            warning_threshold=0.2,
        ),
    )
    governor = QuotaGovernor(policy)
    app = create_app(event_log=event_log, quota_governor=governor)
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
