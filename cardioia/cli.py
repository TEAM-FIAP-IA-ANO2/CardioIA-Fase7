"""CLI do MVP CardioIA."""

import argparse
import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv

from .local_pipeline import run_local
from .schemas import PatientData


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CardioIA - MVP acadêmico")
    parser.add_argument("--case", type=Path, required=True, help="Arquivo JSON do caso sintético")
    parser.add_argument("--mode", choices=["local", "agents"], default="local")
    parser.add_argument("--session-id", default=None)
    parser.add_argument("--output", type=Path, default=None)
    return parser


def main() -> None:
    args = _parser().parse_args()
    root = Path(__file__).resolve().parents[1]
    load_dotenv(root / ".env")
    patient = PatientData.model_validate_json(args.case.read_text(encoding="utf-8"))

    if args.mode == "local":
        response = run_local(patient, root, execution_id=args.session_id)
    else:
        from .agents_pipeline import run_agents
        response = asyncio.run(run_agents(patient, root, session_id=args.session_id))

    text = response.model_dump_json(indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
