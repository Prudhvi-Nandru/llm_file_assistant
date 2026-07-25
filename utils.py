from pathlib import Path
from datetime import datetime


def readable_file_size(size: int) -> str:
    """
    Convert bytes into human-readable units.
    """

    for unit in ["B", "KB", "MB", "GB"]:

        if size < 1024:
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} TB"


def file_metadata(filepath: Path) -> dict:
    """
    Returns metadata for a file.
    """

    stat = filepath.stat()

    return {
        "filename": filepath.name,
        "path": str(filepath),
        "extension": filepath.suffix.lower(),
        "size_bytes": stat.st_size,
        "size": readable_file_size(stat.st_size),
        "modified": datetime.fromtimestamp(
            stat.st_mtime
        ).isoformat(),
    }
