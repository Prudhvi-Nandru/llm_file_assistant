from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    """
    Application configuration.
    """

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    MODEL = os.getenv(
        "MODEL",
        "gpt-4.1"
    )

    MAX_CONTEXT_CHARS = 12000

    DEFAULT_ENCODING = "utf-8"

    SUPPORTED_EXTENSIONS = [
        ".pdf",
        ".docx",
        ".txt",
    ]

    OUTPUT_DIRECTORY = "output"

    RESUME_DIRECTORY = "resumes"