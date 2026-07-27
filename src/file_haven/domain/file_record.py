from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class FileRecord:
    path: Path
    size_bytes: int
    modified_at: datetime

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def parent_folder(self) -> Path:
        return self.path.parent

    @property
    def extension(self) -> str:
        return self.path.suffix.lower()

    @property
    def age_days(self) -> int:
        elapsed = datetime.now() - self.modified_at
        return max(elapsed.days, 0)