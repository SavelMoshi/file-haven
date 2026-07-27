def format_file_size(size_bytes: int) -> str:
    if size_bytes < 0:
        raise ValueError("File size cannot be negative.")

    units = ("B", "KB", "MB", "GB", "TB")
    size = float(size_bytes)

    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"

            return f"{size:.1f} {unit}"

        size /= 1024

    raise RuntimeError("Unable to format file size.")
