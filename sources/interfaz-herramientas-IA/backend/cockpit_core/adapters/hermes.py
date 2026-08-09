"""F1-P3: Hermes adapter — invokes local Hermes CLI as agent runtime."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HermesRunResult:
    run_id: str
    exit_code: int
    stdout: str
    stderr: str
    success: bool


class HermesAdapter:
    """Adapter that invokes the local Hermes CLI in non-interactive mode."""

    def __init__(
        self,
        *,
        hermes_bin: str = "hermes",
        default_model: str = "",
        default_provider: str = "",
    ) -> None:
        self._bin = hermes_bin
        self._model = default_model
        self._provider = default_provider

    def run_query(
        self,
        *,
        query: str,
        model: str | None = None,
        provider: str | None = None,
        toolsets: list[str] | None = None,
        skills: list[str] | None = None,
        max_turns: int | None = None,
        run_id: str = "",
    ) -> HermesRunResult:
        cmd: list[str] = [self._bin, "chat", "-q", query]

        effective_model = model or self._model
        if effective_model:
            cmd.extend(["-m", effective_model])

        effective_provider = provider or self._provider
        if effective_provider:
            cmd.extend(["--provider", effective_provider])

        if toolsets:
            cmd.extend(["-t", ",".join(toolsets)])

        if skills:
            cmd.extend(["-s", ",".join(skills)])

        if max_turns is not None:
            cmd.extend(["--max-turns", str(max_turns)])

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )
            return HermesRunResult(
                run_id=run_id,
                exit_code=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
                success=proc.returncode == 0,
            )
        except subprocess.TimeoutExpired:
            return HermesRunResult(
                run_id=run_id,
                exit_code=-1,
                stdout="",
                stderr="timeout: hermes run exceeded 300s",
                success=False,
            )
        except FileNotFoundError:
            return HermesRunResult(
                run_id=run_id,
                exit_code=-2,
                stdout="",
                stderr=f"hermes binary not found: {self._bin}",
                success=False,
            )

    def health_check(self) -> dict[str, Any]:
        """Verify Hermes CLI is available."""
        try:
            proc = subprocess.run(
                [self._bin, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return {
                "available": proc.returncode == 0,
                "version": proc.stdout.strip(),
            }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {"available": False, "version": ""}
