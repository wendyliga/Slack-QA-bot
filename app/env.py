import os

DEFAULT_SYSTEM_TEXT = """
You are a bot in a slack chat room. You might receive messages from multiple people.
Format bold text *like this*, italic text _like this_ and strikethrough text ~like this~.
Slack user IDs match the regex `<@U.*?>`.
Your Slack user ID is <@{bot_user_id}>.
Each message has the author's Slack user ID prepended, like the regex `^<@U.*?>: ` followed by the message text.
"""
SYSTEM_TEXT = os.environ.get("OPENAI_SYSTEM_TEXT", DEFAULT_SYSTEM_TEXT)


DEFAULT_OPENAI_TIMEOUT_SECONDS = 30
OPENAI_TIMEOUT_SECONDS = int(
    os.environ.get("OPENAI_TIMEOUT_SECONDS", DEFAULT_OPENAI_TIMEOUT_SECONDS)
)

DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)

DEFAULT_OPENAI_TEMPERATURE = 1
OPENAI_TEMPERATURE = float(
    os.environ.get("OPENAI_TEMPERATURE", DEFAULT_OPENAI_TEMPERATURE)
)

MEMORY_DIR = os.environ.get("MEMORY_DIR", "/tmp/memory_dir")
EMBEDDINGS_MODEL_NAME = os.environ.get("EMBEDDINGS_MODEL_NAME", "all-MiniLM-L6-v2")
EMBEDDINGS_SLEEP_TIME = float(os.environ.get("EMBEDDINGS_SLEEP_TIME", 10))
EMBEDDINGS_REQUEST_CONCURRENT_JOB = float(os.environ.get("EMBEDDINGS_REQUEST_CONCURRENT_JOB", 16))
BASE_PATH = os.environ.get("OPENAI_API_BASE", "http://localhost:8080/v1")

USE_SLACK_LANGUAGE = os.environ.get("USE_SLACK_LANGUAGE", "true") == "true"
SLACK_APP_LOG_LEVEL = os.environ.get("SLACK_APP_LOG_LEVEL", "DEBUG")
TRANSLATE_MARKDOWN = os.environ.get("TRANSLATE_MARKDOWN", "false") == "true"
REDACTION_ENABLED = os.environ.get("REDACTION_ENABLED", "false") == "true"

# Redaction patterns
#
REDACT_EMAIL_PATTERN = os.environ.get(
    "REDACT_EMAIL_PATTERN", r"\b[A-Za-z0-9.*%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)
REDACT_PHONE_PATTERN = os.environ.get(
    "REDACT_PHONE_PATTERN", r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
)
REDACT_CREDIT_CARD_PATTERN = os.environ.get(
    "REDACT_CREDIT_CARD_PATTERN", r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"
)
REDACT_SSN_PATTERN = os.environ.get(
    "REDACT_SSN_PATTERN", r"\b\d{3}[- ]?\d{2}[- ]?\d{4}\b"
)
# For REDACT_USER_DEFINED_PATTERN, the default will never match anything
REDACT_USER_DEFINED_PATTERN = os.environ.get("REDACT_USER_DEFINED_PATTERN", r"(?!)")

# data source
GITHUB_PERSONAL_ACCESS_TOKEN=os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
GIT_REPOSITORIES = os.environ.get("GIT_REPOSITORIES", "")
GIT_ISSUE_REPOSITORIES = os.environ.get("GIT_ISSUE_REPOSITORIES", "")

JIRA_API_KEY=os.environ.get("JIRA_API_KEY", "")
CONFLUENCE_BASE_URL=os.environ.get("CONFLUENCE_BASE_URL", "")
CONFLUENCE_SPACE_KEY=os.environ.get("CONFLUENCE_SPACE_KEY", "")
CONFLUENCE_EMAIL=os.environ.get("CONFLUENCE_EMAIL", "")
CONFLUENCE_LIMIT_PER_REQUEST=os.environ.get("CONFLUENCE_LIMIT_PER_REQUEST", "")
CONFLUENCE_TOTAL_LIMIT_PAGES=os.environ.get("CONFLUENCE_TOTAL_LIMIT_PAGES", "")