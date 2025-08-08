from __future__ import annotations

from pathlib import Path
import subprocess
import typer
import psutil

app = typer.Typer(help="RangeForge orchestrator CLI.")

STATE_DIR = Path("state")


def run_cmd(cmd: list[str], cwd: Path | None = None) -> int:
    """Run a command streaming stdout/stderr."""
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert process.stdout
    for line in process.stdout:
        typer.echo(line.rstrip())
    return process.wait()


def check_resources(min_cpu: int = 2, min_ram_gb: int = 8, min_disk_gb: int = 50) -> None:
    """Ensure host has enough CPU, RAM and disk space."""
    cpu = psutil.cpu_count(logical=False) or 0
    ram_gb = psutil.virtual_memory().total / 1024**3
    disk_gb = psutil.disk_usage("/").free / 1024**3
    if cpu < min_cpu or ram_gb < min_ram_gb or disk_gb < min_disk_gb:
        raise RuntimeError(
            "Insufficient resources: "
            f"CPU={cpu}, RAM={ram_gb:.1f}GB, DISK={disk_gb:.1f}GB"
        )


@app.command()
def init() -> None:
    """Initialize Terraform and verify resources."""
    check_resources()
    run_cmd(["terraform", "-chdir=infra/terraform", "init"])


@app.command()
def up(profile: str = typer.Option(..., help="Profile to deploy")) -> None:
    """Provision infrastructure and configure via Ansible."""
    STATE_DIR.mkdir(exist_ok=True)
    run_cmd(["terraform", "-chdir=infra/terraform", "apply", "-auto-approve", f"-var=profile={profile}"])
    with open(STATE_DIR / "inventory.json", "w", encoding="utf-8") as fh:
        subprocess.run(
            ["terraform", "-chdir=infra/terraform", "output", "-json"],
            check=False,
            stdout=fh,
        )
    run_cmd(["ansible-playbook", "site.yml", "-i", str(STATE_DIR / "inventory.json")])


@app.command()
def emulate(playbook: str = typer.Option(..., help="Comma separated playbooks")) -> None:
    """Run attack emulation playbooks."""
    for pb in playbook.split(","):
        run_cmd(["ansible-playbook", f"playbooks/{pb}.yml", "-i", str(STATE_DIR / "inventory.json")])


@app.command()
def observe(
    import_dashboards: bool = typer.Option(
        False, help="Import dashboards into Kibana/Wazuh-Dash"
    )
) -> None:
    """Open dashboards or rules."""
    if import_dashboards:
        from . import import_dashboards as importer

        importer.import_dashboards()
        typer.echo("Dashboards imported")
    else:
        typer.echo("Observation not implemented yet")


@app.command()
def collect(out: Path = typer.Option(Path("./artifacts"), help="Output directory")) -> None:
    """Collect run artifacts (stub)."""
    out.mkdir(parents=True, exist_ok=True)
    typer.echo(f"Artifacts collected into {out}")


@app.command()
def down() -> None:
    """Destroy infrastructure."""
    run_cmd(["terraform", "-chdir=infra/terraform", "destroy", "-auto-approve"])


@app.command()
def version() -> None:
    """Show version information."""
    typer.echo("RangeForge orchestrator 0.1.0")


if __name__ == "__main__":
    app()
