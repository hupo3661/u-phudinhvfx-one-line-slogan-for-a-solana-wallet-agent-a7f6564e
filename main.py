#!/usr/bin/env python3
"""Write the entry text to $MAKEFUN_OUTPUT_DIR/entry.txt (default /output/entry.txt).

The entry is a single line of text. This program validates it before writing
(single line, non-empty, within the competition's character and word limits),
writes it, then reads the file back and checks it byte for byte.
"""

import hashlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path

ENTRY = 'Your Solana wallet, finally with a brain: it signs, swaps, and never sleeps, so you can.'


@dataclass(frozen=True)
class EntryLimits:
    """Competition limits for the one-line entry."""

    max_chars: int = 140
    max_words: int = 20


LIMITS = EntryLimits()

DEFAULT_OUTPUT_DIR = "/output"
OUTPUT_FILENAME = "entry.txt"


def check_non_empty(text: str) -> str | None:
    """Return an error message if the entry is empty, else None."""
    if not text or not text.strip():
        return "error: entry is empty"
    return None


def check_single_line(text: str) -> str | None:
    """Return an error message if the entry spans more than one line, else None."""
    if "\n" in text or "\r" in text:
        return "error: entry must be a single line"
    return None


def check_char_limit(text: str) -> str | None:
    """Return an error message if the entry exceeds the char limit."""
    if len(text) > LIMITS.max_chars:
        return (
            f"error: entry is {len(text)} chars, "
            f"over the {LIMITS.max_chars} limit"
        )
    return None


def check_word_limit(text: str) -> str | None:
    """Return an error message if the entry exceeds the word limit."""
    word_count = len(text.split())
    if LIMITS.max_words is not None and word_count > LIMITS.max_words:
        return f"error: entry is {word_count} words, over the {LIMITS.max_words} limit"
    return None


def check_limits(text: str) -> str | None:
    """Return an error message if the entry exceeds the char or word limit."""
    for check in (check_char_limit, check_word_limit):
        error = check(text)
        if error is not None:
            return error
    return None


def validate_entry(text: str) -> str | None:
    """Run every entry check in order; return the first error, or None."""
    for check in (check_non_empty, check_single_line, check_limits):
        error = check(text)
        if error is not None:
            return error
    return None


def resolve_output_path() -> Path:
    """Resolve the entry file path from $MAKEFUN_OUTPUT_DIR."""
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
    return Path(out_dir) / OUTPUT_FILENAME


def write_entry(path: Path, text: str) -> None:
    """Write the entry plus a trailing newline, creating the directory first."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n", encoding="utf-8", newline="\n")


def verify_written(path: Path, text: str) -> bool:
    """Re-read the file and confirm its bytes match the entry exactly.

    Two independent checks: direct byte equality, and a sha256 digest
    comparison, so a mismatch cannot slip through either one alone.
    """
    expected = (text + "\n").encode("utf-8")
    actual = path.read_bytes()
    if actual != expected:
        return False
    return hashlib.sha256(actual).hexdigest() == hashlib.sha256(expected).hexdigest()


def main() -> int:
    text = ENTRY
    error = validate_entry(text)
    if error is not None:
        print(error, file=sys.stderr)
        return 1
    path = resolve_output_path()
    write_entry(path, text)
    if not verify_written(path, text):
        print(
            "error: written file does not match the entry byte for byte",
            file=sys.stderr,
        )
        return 1
    print(text)
    print(f"wrote {len(text)} chars to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
