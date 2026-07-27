import pytest

from file_haven.services import format_file_size


@pytest.mark.parametrize(
    ("size_bytes", "expected"),
    [
        (0, "0 B"),
        (512, "512 B"),
        (1024, "1.0 KB"),
        (1536, "1.5 KB"),
        (1024**2, "1.0 MB"),
        (1024**3, "1.0 GB"),
        (1024**4, "1.0 TB"),
    ],
)
def test_format_file_size(
    size_bytes: int,
    expected: str,
) -> None:
    assert format_file_size(size_bytes) == expected


def test_format_file_size_rejects_negative_values() -> None:
    with pytest.raises(
        ValueError,
        match="File size cannot be negative",
    ):
        format_file_size(-1)
