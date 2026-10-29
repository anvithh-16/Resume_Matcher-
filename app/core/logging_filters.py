import logging
import re

PATTERNS = [
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]+"),
    re.compile(r"(?i)(password|passwd|secret|api[_-]?key|token)\s*[=:]\s*\S+"),
]

def redact(text: str) -> str:
    for p in PATTERNS:
        text = p.sub("[REDACTED]", text)
    return text

class RedactFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.name == "uvicorn.access":
            # Uvicorn's access formatter unpacks record.args, so redact each arg and keep the tuple.
            record.args = tuple(redact(a) if isinstance(a, str) else a for a in record.args)
            return True
        record.msg, record.args = redact(record.getMessage()), ()
        return True
