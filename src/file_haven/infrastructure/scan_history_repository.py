import sqlite3
from datetime import datetime
from pathlib import Path

from file_haven.domain import ScanHistoryRecord


class ScanHistoryRepository:
    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path
        self._create_table()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._database_path)

    def _create_table(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    folder TEXT NOT NULL,
                    file_count INTEGER NOT NULL,
                    scanned_at TEXT NOT NULL
                )
                """
            )

    def add(self, record: ScanHistoryRecord) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO scan_history (
                    folder,
                    file_count,
                    scanned_at
                )
                VALUES (?, ?, ?)
                """,
                (
                    str(record.folder),
                    record.file_count,
                    record.scanned_at.isoformat(),
                ),
            )

    def get_all(self) -> list[ScanHistoryRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT folder, file_count, scanned_at
                FROM scan_history
                ORDER BY scanned_at DESC
                """
            ).fetchall()

        return [
            ScanHistoryRecord(
                folder=Path(folder),
                file_count=file_count,
                scanned_at=datetime.fromisoformat(scanned_at),
            )
            for folder, file_count, scanned_at in rows
        ]
