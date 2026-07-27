from datetime import datetime, timedelta
from pathlib import Path

from file_haven.domain import FileRecord


def test_file_record_exposes_file_information() -> None:
    record = FileRecord(
        path=Path("/Users/example/Documents/report.PDF"),
        size_bytes=2048,
        modified_at=datetime.now(),
    )

    assert record.name == "report.PDF"
    assert record.parent_folder == Path("/Users/example/Documents")
    assert record.extension == ".pdf"


def test_file_record_calculates_age_in_days() -> None:
    record = FileRecord(
        path=Path("/Users/example/old-file.txt"),
        size_bytes=100,
        modified_at=datetime.now() - timedelta(days=30),
    )

    assert record.age_days == 30


def test_file_record_age_cannot_be_negative() -> None:
    record = FileRecord(
        path=Path("/Users/example/future-file.txt"),
        size_bytes=100,
        modified_at=datetime.now() + timedelta(days=5),
    )

    assert record.age_days == 0
