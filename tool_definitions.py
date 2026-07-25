TOOLS = [

    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read a TXT, PDF, or DOCX resume file and return extracted "
                "text content with metadata."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the resume file."
                    }
                },
                "required": ["filepath"],
                "additionalProperties": False
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": (
                "List files in a directory and return filename, extension, "
                "size, modified date, and path metadata."
            ),
            "parameters": {
                "type": "object",
                "properties": {

                    "directory": {
                        "type": "string",
                        "description": "Directory to list, such as resumes."
                    },

                    "extension": {
                        "type": "string",
                        "description": (
                            "Optional extension filter such as .pdf, pdf, "
                            ".txt, or docx."
                        )
                    }

                },

                "required": [
                    "directory"
                ],
                "additionalProperties": False
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Write text content to a file, creating parent directories "
                "when needed."
            ),
            "parameters": {
                "type": "object",
                "properties": {

                    "filepath": {
                        "type": "string",
                        "description": "Destination file path."
                    },

                    "content": {
                        "type": "string",
                        "description": "Text content to write."
                    }

                },

                "required": [
                    "filepath",
                    "content"
                ],
                "additionalProperties": False
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "search_in_file",
            "description": (
                "Search case-insensitively for a keyword in one resume file "
                "and return matches with surrounding context."
            ),
            "parameters": {
                "type": "object",
                "properties": {

                    "filepath": {
                        "type": "string",
                        "description": "Path to the file to search."
                    },

                    "keyword": {
                        "type": "string",
                        "description": "Keyword or phrase to find."
                    }

                },

                "required": [
                    "filepath",
                    "keyword"
                ],
                "additionalProperties": False
            }
        }
    }

]
