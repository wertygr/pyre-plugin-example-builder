import fnmatch
from pathlib import Path


def fake_post(error, _) -> None:
    print(error)

def is_blacklisted(path: Path, blacklist: list[str]) -> bool:
    return any(
        fnmatch.fnmatch(part, pattern)
        for part in path.parts
        for pattern in blacklist
    )