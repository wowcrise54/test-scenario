from pathlib import Path
import sys
import uuid

sys.path.append(str(Path(__file__).resolve().parents[1]))
from orchestrator.attack_runner import AttackRunner, LocalExecutor


PLAYBOOK_DIR = Path("attack_playbooks")


def test_reference_playbooks(tmp_path: Path) -> None:
    executor = LocalExecutor()
    runner = AttackRunner(executor, log_dir=tmp_path)
    for name in ["kerberoasting", "lateral_psexec", "dcsync"]:
        playbook = PLAYBOOK_DIR / f"{name}.yml"
        run_id = str(uuid.uuid4())
        runner.run_playbook(playbook, range_run_id=run_id, safe=True)
        log_file = tmp_path / f"{run_id}.log"
        assert log_file.exists()
        assert run_id in log_file.read_text()
