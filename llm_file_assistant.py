from __future__ import annotations

import argparse
import json
from json import JSONDecodeError
from typing import Any

from rich.console import Console

from config import Config
from fs_tools import list_files
from fs_tools import read_file
from fs_tools import search_in_file
from fs_tools import write_file
from prompts import SYSTEM_PROMPT
from tool_definitions import TOOLS

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - exercised only without dependencies
    OpenAI = None


console = Console()

AVAILABLE_FUNCTIONS = {
    "read_file": read_file,
    "list_files": list_files,
    "write_file": write_file,
    "search_in_file": search_in_file,
}


def _message_to_dict(message: Any) -> dict[str, Any]:
    """Convert OpenAI SDK message objects into plain dictionaries."""

    if hasattr(message, "model_dump"):
        return message.model_dump(exclude_none=True)

    if isinstance(message, dict):
        return message

    raise TypeError(f"Unsupported message type: {type(message)!r}")


def create_client() -> OpenAI:
    """Create an OpenAI client with a helpful configuration error."""

    if OpenAI is None:
        raise RuntimeError(
            "The OpenAI SDK is not installed. Run `pip install -r requirements.txt`."
        )

    if not Config.OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Create a .env file or export the variable."
        )

    return OpenAI(api_key=Config.OPENAI_API_KEY)


def execute_tool(tool_call: Any) -> dict[str, Any]:
    """Execute one LLM-requested filesystem tool call."""

    name = tool_call.function.name

    if name not in AVAILABLE_FUNCTIONS:
        return {
            "success": False,
            "error": f"Unknown tool: {name}",
        }

    try:
        arguments = json.loads(tool_call.function.arguments or "{}")
    except JSONDecodeError as exc:
        return {
            "success": False,
            "error": f"Invalid tool arguments: {exc}",
        }

    try:
        return AVAILABLE_FUNCTIONS[name](**arguments)
    except TypeError as exc:
        return {
            "success": False,
            "error": f"Invalid arguments for {name}: {exc}",
        }
    except Exception as exc:  # pragma: no cover - defensive boundary
        return {
            "success": False,
            "error": str(exc),
        }


def ask_llm(
        user_query: str,
        client: OpenAI,
        max_tool_rounds: int = 5
) -> str:
    """
    Send a user query to the LLM and let it call filesystem tools as needed.
    """

    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_query,
        },
    ]

    for _ in range(max_tool_rounds):
        response = client.chat.completions.create(
            model=Config.MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message
        messages.append(_message_to_dict(assistant_message))

        if not assistant_message.tool_calls:
            return assistant_message.content or ""

        for tool_call in assistant_message.tool_calls:
            result = execute_tool(tool_call)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=True),
                }
            )

    return (
        "I reached the maximum number of tool-call rounds before completing "
        "the request. Try narrowing the question."
    )


def run_interactive(client: OpenAI) -> None:
    """Run the command-line chat loop."""

    console.print("\n[bold green]LLM Resume Assistant[/bold green]")
    console.print("Type 'exit' or 'quit' to stop.\n")

    while True:
        question = input("\nYou: ").strip()

        if question.lower() in {"exit", "quit"}:
            break

        if not question:
            continue

        answer = ask_llm(question, client)
        console.print("\nAssistant:\n")
        console.print(answer)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="LLM-powered resume file assistant."
    )
    parser.add_argument(
        "--message",
        "-m",
        help="Run one request and print the answer instead of starting chat.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        client = create_client()
    except RuntimeError as exc:
        console.print(f"[bold red]Configuration error:[/bold red] {exc}")
        raise SystemExit(1) from exc

    if args.message:
        console.print(ask_llm(args.message, client))
        return

    run_interactive(client)


if __name__ == "__main__":
    main()
