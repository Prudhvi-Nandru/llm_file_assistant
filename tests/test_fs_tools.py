from __future__ import annotations

from pathlib import Path

from fs_tools import list_files
from fs_tools import read_file
from fs_tools import search_in_file
from fs_tools import write_file


def test_read_file_extracts_txt_content_and_metadata(tmp_path: Path) -> None:
    resume = tmp_path / "resume.txt"
    resume.write_text("Jane Doe\nPython developer", encoding="utf-8")

    result = read_file(str(resume))

    assert result["success"] is True
    assert "Python developer" in result["content"]
    assert result["metadata"]["filename"] == "resume.txt"
    assert result["metadata"]["extension"] == ".txt"
    assert result["metadata"]["size_bytes"] > 0
    assert "modified" in result["metadata"]


def test_list_files_filters_by_extension_without_leading_dot(
        tmp_path: Path
) -> None:
    (tmp_path / "resume_a.txt").write_text("A", encoding="utf-8")
    (tmp_path / "resume_b.pdf").write_text("B", encoding="utf-8")
    (tmp_path / "notes.md").write_text("C", encoding="utf-8")

    results = list_files(str(tmp_path), "txt")

    assert [item["filename"] for item in results] == ["resume_a.txt"]
    assert results[0]["extension"] == ".txt"


def test_write_file_creates_parent_directories(tmp_path: Path) -> None:
    destination = tmp_path / "nested" / "summary.txt"

    result = write_file(str(destination), "Short summary")

    assert result["success"] is True
    assert destination.read_text(encoding="utf-8") == "Short summary"
    assert result["bytes_written"] == len("Short summary".encode("utf-8"))
    assert result["metadata"]["filename"] == "summary.txt"


def test_search_in_file_is_case_insensitive_with_context(tmp_path: Path) -> None:
    resume = tmp_path / "resume.txt"
    resume.write_text(
        "Led API projects. Built production PYTHON services. Mentored team.",
        encoding="utf-8",
    )

    result = search_in_file(str(resume), "python")

    assert result["success"] is True
    assert result["count"] == 1
    assert result["matches"][0]["match"] == "PYTHON"
    assert "production PYTHON services" in result["matches"][0]["context"]


def test_search_rejects_empty_keyword(tmp_path: Path) -> None:
    resume = tmp_path / "resume.txt"
    resume.write_text("Python", encoding="utf-8")

    result = search_in_file(str(resume), " ")

    assert result["success"] is False
    assert result["count"] == 0
    assert "keyword" in result["error"]


def test_read_file_returns_error_for_unsupported_extension(
        tmp_path: Path
) -> None:
    resume = tmp_path / "resume.md"
    resume.write_text("Markdown resume", encoding="utf-8")

    result = read_file(str(resume))

    assert result["success"] is False
    assert result["content"] == ""
    assert "Unsupported extension" in result["error"]
