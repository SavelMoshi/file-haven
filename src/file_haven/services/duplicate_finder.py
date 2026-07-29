from collections import defaultdict
from collections.abc import Iterable
from hashlib import sha256
from pathlib import Path

from file_haven.domain import DuplicateGroup, FileRecord


class DuplicateFinder:
    """Find duplicate files using size grouping and SHA-256 hashing."""

    CHUNK_SIZE = 1024 * 1024

    def find(
        self,
        records: Iterable[FileRecord],
    ) -> list[DuplicateGroup]:
        files_by_size: dict[int, list[FileRecord]] = defaultdict(list)

        for record in records:
            if record.size_bytes > 0:
                files_by_size[record.size_bytes].append(record)

        duplicate_groups: list[DuplicateGroup] = []

        for same_size_files in files_by_size.values():
            if len(same_size_files) < 2:
                continue

            files_by_hash: dict[str, list[FileRecord]] = defaultdict(list)

            for record in same_size_files:
                try:
                    fingerprint = self._hash_file(record.path)
                except (FileNotFoundError, PermissionError, OSError):
                    continue

                files_by_hash[fingerprint].append(record)

            for fingerprint, matching_files in files_by_hash.items():
                if len(matching_files) < 2:
                    continue

                duplicate_groups.append(
                    DuplicateGroup(
                        fingerprint=fingerprint,
                        files=tuple(matching_files),
                    )
                )

        duplicate_groups.sort(
            key=lambda group: group.reclaimable_bytes,
            reverse=True,
        )

        return duplicate_groups

    def _hash_file(self, path: Path) -> str:
        hasher = sha256()

        with path.open("rb") as file:
            while chunk := file.read(self.CHUNK_SIZE):
                hasher.update(chunk)

        return hasher.hexdigest()
