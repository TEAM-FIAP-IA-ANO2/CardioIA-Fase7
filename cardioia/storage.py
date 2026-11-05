"""Persistência SQLite simples, portátil e transacional."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from .schemas import FinalResponse, ReadingHistoryItem, SensorReading

DDL = """
CREATE TABLE IF NOT EXISTS readings (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 device_id TEXT NOT NULL,
 captured_at TEXT NOT NULL,
 received_at TEXT NOT NULL,
 payload_json TEXT NOT NULL,
 probability REAL NOT NULL,
 risk_band TEXT NOT NULL,
 analysis_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_readings_device_time ON readings(device_id, captured_at DESC);
"""

class ReadingRepository:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.executescript(DDL)

    def _connect(self):
        con = sqlite3.connect(self.path, timeout=10)
        con.row_factory = sqlite3.Row
        return con

    def save(self, reading: SensorReading, analysis: FinalResponse) -> int:
        with self._connect() as con:
            cur = con.execute(
                "INSERT INTO readings(device_id,captured_at,received_at,payload_json,probability,risk_band,analysis_json) VALUES(?,?,?,?,?,?,?)",
                (reading.device_id, reading.captured_at.isoformat(), datetime.now(timezone.utc).isoformat(), reading.model_dump_json(), analysis.probability, analysis.risk_band, analysis.model_dump_json()),
            )
            con.commit()
            return int(cur.lastrowid)

    def history(self, limit: int = 50, device_id: str | None = None) -> list[ReadingHistoryItem]:
        sql = "SELECT * FROM readings"
        args: list[object] = []
        if device_id:
            sql += " WHERE device_id = ?"
            args.append(device_id)
        sql += " ORDER BY captured_at DESC LIMIT ?"
        args.append(limit)
        with self._connect() as con:
            rows = con.execute(sql, args).fetchall()
        items = []
        for row in rows:
            reading = SensorReading.model_validate_json(row["payload_json"])
            items.append(ReadingHistoryItem(
                reading_id=row["id"], device_id=row["device_id"], captured_at=datetime.fromisoformat(row["captured_at"]), received_at=datetime.fromisoformat(row["received_at"]), probability=row["probability"], risk_band=row["risk_band"], payload=reading.patient_data(),
            ))
        return items

    def latest_analysis(self, device_id: str | None = None) -> tuple[int, SensorReading, FinalResponse] | None:
        sql = "SELECT * FROM readings"
        args: list[object] = []
        if device_id:
            sql += " WHERE device_id = ?"
            args.append(device_id)
        sql += " ORDER BY captured_at DESC LIMIT 1"
        with self._connect() as con:
            row = con.execute(sql, args).fetchone()
        if row is None:
            return None
        return row["id"], SensorReading.model_validate_json(row["payload_json"]), FinalResponse.model_validate_json(row["analysis_json"])
