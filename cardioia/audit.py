"""Trilha de auditoria sem duplicar dados sensíveis."""
import hashlib
import json
from pathlib import Path
from pydantic import BaseModel
from .schemas import AuditRecord

def fingerprint(value: BaseModel) -> str:
    canonical = json.dumps(value.model_dump(mode="json"), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def append_record(path: Path, record: AuditRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(record.model_dump_json() + "\n")


def read_records(path: Path) -> list[dict]:
    """Lê a trilha JSONL; linhas vazias são ignoradas."""
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
