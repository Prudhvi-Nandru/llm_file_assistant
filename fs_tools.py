from __future__ import annotations

import logging
import re

from pathlib import Path
from typing import Any
from typing import Optional

from config import Config
from utils import file_metadata

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)


# ---------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------

def _read_txt(filepath: Path) -> str:
    """Read text file."""

    return filepath.read_text(
        encoding=Config.DEFAULT_ENCODING,
        errors="replace"
    )


def _read_docx(filepath: Path) -> str:
    """Extract text from DOCX."""

    try:
        from docx import Document
    except ImportError as exc:
        raise RuntimeError(
            "DOCX support requires python-docx. Install dependencies with "
            "`pip install -r requirements.txt`."
        ) from exc

    document = Document(filepath)

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    return "\n".join(paragraphs)


def _read_pdf(filepath: Path) -> str:
    """Extract text from PDF."""

    try:
        from PyPDF2 import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "PDF support requires PyPDF2. Install dependencies with "
            "`pip install -r requirements.txt`."
        ) from exc

    reader = PdfReader(str(filepath))

    pages = []

    for page in reader.pages:
        pages.append(page.extract_text() or "")

    return "\n".join(pages)


def _normalise_extension(extension: Optional[str]) -> Optional[str]:
    """Return a lower-case extension with a leading dot."""

    if not extension:
        return None

    cleaned = extension.strip().lower()

    if not cleaned:
        return None

    return cleaned if cleaned.startswith(".") else f".{cleaned}"


def _validate_file(filepath: Path) -> None:

    if not filepath.exists():
        raise FileNotFoundError(
            f"{filepath} does not exist."
        )

    if not filepath.is_file():
        raise ValueError(
            f"{filepath} is not a file."
        )

    if filepath.suffix.lower() not in Config.SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported extension: {filepath.suffix}"
        )


# ---------------------------------------------------------
# Public APIs
# ---------------------------------------------------------

def read_file(filepath: str) -> dict[str, Any]:
    """
    Read a TXT, PDF, or DOCX file and return extracted text plus metadata.

    Returns
    -------
    dict
        {
            "success": bool,
            "content": str,
            "metadata": dict,
            "error": str | None
        }
    """

    path = Path(filepath).expanduser()

    try:

        _validate_file(path)

        extension = path.suffix.lower()

        if extension == ".txt":
            text = _read_txt(path)

        elif extension == ".docx":
            text = _read_docx(path)

        elif extension == ".pdf":
            text = _read_pdf(path)

        else:
            raise ValueError(
                "Unsupported file type."
            )

        return {
            "success": True,
            "content": text,
            "metadata": file_metadata(path)
        }

    except Exception as ex:

        logging.error(ex)

        return {
            "success": False,
            "content": "",
            "metadata": {},
            "error": str(ex)
        }


# ---------------------------------------------------------

def list_files(
        directory: str,
        extension: Optional[str] = None
) -> list[dict[str, Any]]:
    """
    List files inside a directory, optionally filtered by extension.

    Parameters
    ----------
    directory : str

    extension : Optional[str]

    Returns
    -------
    list
    """

    directory_path = Path(directory).expanduser()
    expected_extension = _normalise_extension(extension)

    if not directory_path.exists() or not directory_path.is_dir():
        return []

    files = []

    for file in directory_path.iterdir():

        if not file.is_file():
            continue

        if expected_extension:

            if file.suffix.lower() != expected_extension:
                continue

        files.append(file_metadata(file))

    files.sort(
        key=lambda x: x["filename"]
    )

    return files


# ---------------------------------------------------------

def write_file(
        filepath: str,
        content: str
) -> dict[str, Any]:
    """
    Write content to disk.

    Creates directories automatically.
    """

    try:

        path = Path(filepath).expanduser()

        if path.exists() and path.is_dir():
            raise IsADirectoryError(
                f"{path} is a directory, not a file path."
            )

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        path.write_text(
            content,
            encoding=Config.DEFAULT_ENCODING
        )

        return {
            "success": True,
            "filepath": str(path),
            "bytes_written": len(
                content.encode(Config.DEFAULT_ENCODING)
            ),
            "metadata": file_metadata(path)
        }

    except Exception as ex:

        logging.error(ex)

        return {
            "success": False,
            "error": str(ex)
        }


# ---------------------------------------------------------

def search_in_file(
        filepath: str,
        keyword: str
) -> dict[str, Any]:
    """
    Case-insensitive keyword search.

    Returns surrounding context.
    """

    if not keyword or not keyword.strip():
        return {
            "success": False,
            "keyword": keyword,
            "count": 0,
            "matches": [],
            "metadata": {},
            "error": "keyword must not be empty"
        }

    result = read_file(filepath)

    if not result["success"]:
        return {
            "success": False,
            "keyword": keyword,
            "count": 0,
            "matches": [],
            "metadata": result.get("metadata", {}),
            "error": result.get("error", "Unable to read file")
        }

    text = result["content"]

    pattern = re.compile(
        re.escape(keyword),
        re.IGNORECASE
    )

    matches = []

    for match in pattern.finditer(text):

        start = max(
            match.start() - 80,
            0
        )

        end = min(
            match.end() + 80,
            len(text)
        )

        context = text[start:end]

        matches.append(
            {
                "match": match.group(),
                "position": match.start(),
                "context": context
            }
        )

    return {

        "success": True,

        "keyword": keyword,

        "count": len(matches),

        "matches": matches,

        "metadata": result["metadata"]
    }


# ---------------------------------------------------------

if __name__ == "__main__":

    print("\nReading TXT")

    print(
        read_file(
            "resumes/carlos_rivera_backend_engineer.txt"
        )
    )

    print("\nListing Files")

    print(
        list_files(
            "resumes"
        )
    )

    print("\nSearching")

    print(
        search_in_file(
            "resumes/carlos_rivera_backend_engineer.txt",
            "python"
        )
    )
