import os

DEFAULT_SYSTEM_TEXT = """
"""

SYSTEM_TEXT = os.environ.get("OPENAI_SYSTEM_TEXT", DEFAULT_SYSTEM_TEXT)

DEFAULT_OPENAI_TIMEOUT_SECONDS = 30
OPENAI_TIMEOUT_SECONDS = int(
    os.environ.get("OPENAI_TIMEOUT_SECONDS", DEFAULT_OPENAI_TIMEOUT_SECONDS)
)

DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)

USE_SLACK_LANGUAGE = os.environ.get("USE_SLACK_LANGUAGE", "true") == "true"

SLACK_APP_LOG_LEVEL = os.environ.get("SLACK_APP_LOG_LEVEL", "DEBUG")

TRANSLATE_MARKDOWN = os.environ.get("TRANSLATE_MARKDOWN", "false") == "true"

MEMORY_DIR = os.environ.get("MEMORY_DIR", "/tmp/memory_dir")
KNOWLEDGEBASE = os.environ.get("MEMORY_DIR", "/tmp/knowledgebase")
MEMORY_DIR_TRAIN = os.environ.get("MEMORY_DIR", "/tmp/dataset")

BASE_PATH = os.environ.get('OPENAI_API_BASE', 'http://localhost:8080/v1')
