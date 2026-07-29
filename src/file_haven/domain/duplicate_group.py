from dataclasses import dataclass

from file_haven.domain.file_record import FileRecord


@dataclass(frozen=True, slots=True)
class DuplicateGroup:
    """A group of files with identical contents."""

    fingerprint: str
    files: tuple[FileRecord, ...]

    @property
    def file_size(self) -> int:
        return self.files[0].size_bytes

    @property
    def reclaimable_bytes(self) -> int:
        return self.file_size * (len(self.files) - 1)
