# LLM File Assistant

Python file assistant for reading, searching, listing, and writing resume files
through structured tools that can be called by an LLM.

## Features

- Read `.txt`, `.pdf`, and `.docx` resume files.
- Return extracted text with file metadata.
- List files in a directory with optional extension filtering.
- Write text files and create parent directories automatically.
- Search files case-insensitively and return surrounding match context.
- Expose the tools to an OpenAI chat model through function calling.

## Project Structure

```text
.
|-- fs_tools.py              # Core filesystem tools
|-- llm_file_assistant.py    # LLM tool-calling CLI
|-- tool_definitions.py      # OpenAI function schemas
|-- prompts.py               # System prompt for tool use
|-- config.py                # Environment-based configuration
|-- resumes/                 # Dummy resume files
|-- output/                  # Generated summaries/reports
|-- tests/                   # Tool tests
|-- requirements.txt
`-- README.md
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Create a `.env` file for LLM usage:

```env
OPENAI_API_KEY=your_api_key_here
MODEL=gpt-4.1
```

The core tools in `fs_tools.py` can be used without an API key.

## Usage

Run the interactive assistant:

```bash
python llm_file_assistant.py
```

Run one prompt from the command line:

```bash
python llm_file_assistant.py --message "Find resumes mentioning Python experience"
```

Example prompts:

```text
Read all resumes in the resumes folder
Find resumes mentioning Python experience
Create a summary file for resumes/carlos_rivera_backend_engineer.txt
List only PDF resumes in the resumes folder
```

Use the tools directly:

```python
from fs_tools import list_files, read_file, search_in_file, write_file

files = list_files("resumes", ".txt")
resume = read_file("resumes/carlos_rivera_backend_engineer.txt")
matches = search_in_file("resumes/carlos_rivera_backend_engineer.txt", "python")
result = write_file("output/carlos_summary.txt", "Carlos has Python API experience.")
```

## Sample Data

The `resumes/` folder includes seven dummy resumes:

- Five TXT resumes.
- One DOCX resume.
- One PDF resume.

They are intentionally small and safe to use for local testing.

## Tests

```bash
python -m pytest
```

The tests validate the core acceptance criteria for TXT reads, metadata,
extension filtering, nested writes, keyword search context, and error handling.

## Notes

- PDF extraction depends on `PyPDF2`.
- DOCX extraction depends on `python-docx`.
- The assistant uses OpenAI tool calling and requires `OPENAI_API_KEY`.
- Generated summaries or reports should be written under `output/`.
