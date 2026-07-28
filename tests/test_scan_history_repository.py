from datetime import datetime
from pathlib import Path

from file_haven.domain import ScanHistoryRecord
from file_haven.infrastructure import ScanHistoryRepository


def test_repository_saves_and_loads_scan_history(
    tmp_path: Path,
) -> None:
    repository = ScanHistoryRepository(tmp_path / "history.db")

    record = ScanHistoryRecord(
        folder=Path("/Users/test/Documents"),
        file_count=125,
        scanned_at=datetime(2026, 7, 28, 12, 30),
    )

    repository.add(record)

    results = repository.get_all()

    assert len(results) == 1
    assert results[0] == record
