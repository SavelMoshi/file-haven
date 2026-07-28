from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ScanHistoryRecord:
    folder: Path
    file_count: int
    scanned_at: datetime
