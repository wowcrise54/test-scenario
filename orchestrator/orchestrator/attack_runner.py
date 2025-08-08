from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, TYPE_CHECKING
import uuid

import yaml
from . import steps

if TYPE_CHECKING:  # pragma: no cover - optional imports for type checking
    from pypsrp.client import Client as WinRMClient  # type: ignore[import-not-found]
    import paramiko
else:  # pragma: no cover
    WinRMClient = Any  # type: ignore
    paramiko = Any  # type: ignore


@dataclass
class AttackPlaybook:
    id: str
    tactic: str
    name: str
    steps: Dict[str, list[dict[str, Any]]]

    @staticmethod
    def from_path(path: Path) -> "AttackPlaybook":
        data = yaml.safe_load(path.read_text())
        return AttackPlaybook(
            id=data["id"],
            tactic=data["tactic"],
            name=data["name"],
            steps=data.get("steps", {}),
        )


class Executor:
    """Base executor interface."""

    def run(self, command: str) -> str:  # pragma: no cover - interface
        raise NotImplementedError


class WinRMExecutor(Executor):
    """Execute PowerShell commands over WinRM using pypsrp."""

    def __init__(self, host: str, username: str, password: str):
        self.client = WinRMClient(host, username=username, password=password, ssl=False)

    def run(self, command: str) -> str:
        stdout, stderr, rc = self.client.execute_ps(command)
        if rc != 0:
            raise RuntimeError(str(stderr))
        return str(stdout)


class SSHExecutor(Executor):
    """Execute shell commands over SSH using paramiko."""

    def __init__(self, host: str, username: str, password: str):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=host, username=username, password=password)

    def run(self, command: str) -> str:
        stdin, stdout, stderr = self.client.exec_command(command)
        err = stderr.read().decode()
        if err:
            raise RuntimeError(err)
        return str(stdout.read().decode())


class LocalExecutor(Executor):
    """Local executor used for tests or simulation."""

    def run(self, command: str) -> str:
        import subprocess

        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        return result.stdout


class AttackRunner:
    """Run ATT&CK playbooks with precheck/exec/cleanup phases."""

    def __init__(self, executor: Executor, log_dir: Path):
        self.executor = executor
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _log(self, range_run_id: str, message: str) -> None:
        log_file = self.log_dir / f"{range_run_id}.log"
        with log_file.open("a", encoding="utf-8") as fh:
            fh.write(f"[{range_run_id}] {message}\n")

    def run_playbook(self, path: Path, range_run_id: str | None = None, *, safe: bool = False) -> None:
        playbook = AttackPlaybook.from_path(path)
        run_id = range_run_id or str(uuid.uuid4())
        for phase in ("precheck", "exec", "cleanup"):
            for step in playbook.steps.get(phase, []):
                action = step["action"]
                args = step.get("args", {})
                func = getattr(steps, action)
                output = func(self.executor, safe=safe, **args)
                self._log(run_id, f"{playbook.id} {phase}:{action} -> {output.strip()}")
