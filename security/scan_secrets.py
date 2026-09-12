from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SECRET_ASSIGNMENT = re.compile(
    r"""(?ix)
    (?P<key>
        api[_-]?key|secret[_-]?key|access[_-]?token|refresh[_-]?token|
        client[_-]?secret|private[_-]?key|password
    )
    \s*[:=]\s*
    (?P<quote>['"])
    (?P<value>[A-Za-z0-9_./+=:@%-]{12,})
    (?P=quote)
    """
)

KNOWN_TOKEN_PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    re.compile(r"gh[pousr]_[0-9A-Za-z_]{36,255}"),
    re.compile(r"xox[baprs]-[0-9A-Za-z-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{32,}"),
]

SKIPPED_DIRECTORIES = {
    ".git",
    ".terraform",
    ".venv",
    "__pycache__",
    "node_modules",
    "quarantine",
}

SCANNED_SUFFIXES = {
    ".env",
    ".json",
    ".js",
    ".jsx",
    ".md",
    ".py",
    ".tf",
    ".tfvars",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}


@dataclass(frozen=True)
class Finding:
    path: str
    line_number: int
    rule: str
    evidence: str


def shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    length = len(value)
    return -sum(
        (value.count(char) / length) * math.log2(value.count(char) / length) for char in set(value)
    )


def should_scan(path: Path) -> bool:
    if any(part in SKIPPED_DIRECTORIES for part in path.parts):
        return False
    return path.name == ".env" or path.suffix.lower() in SCANNED_SUFFIXES


def iter_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and should_scan(path):
            files.append(path)
        elif path.is_dir():
            files.extend(
                child for child in path.rglob("*") if child.is_file() and should_scan(child)
            )
    return sorted(set(files))


def mask(value: str) -> str:
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def scan_file(path: Path, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return findings

    for line_number, line in enumerate(lines, start=1):
        for match in SECRET_ASSIGNMENT.finditer(line):
            value = match.group("value")
            if shannon_entropy(value) >= 3.2:
                findings.append(
                    Finding(
                        path=str(path.relative_to(root)),
                        line_number=line_number,
                        rule="hardcoded-secret-assignment",
                        evidence=f"{match.group('key')}={mask(value)}",
                    )
                )
        for pattern in KNOWN_TOKEN_PATTERNS:
            for match in pattern.finditer(line):
                findings.append(
                    Finding(
                        path=str(path.relative_to(root)),
                        line_number=line_number,
                        rule="known-token-pattern",
                        evidence=mask(match.group(0)),
                    )
                )
    return findings


def write_quarantine(findings: list[Finding], quarantine_dir: Path) -> None:
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "rejected",
        "reason": "raw hardcoded credential patterns detected",
        "finding_count": len(findings),
        "findings": [finding.__dict__ for finding in findings],
    }
    (quarantine_dir / "secret-findings.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed raw secret scanner.")
    parser.add_argument("--paths", nargs="+", required=True, help="Files or directories to scan.")
    parser.add_argument(
        "--quarantine-dir", default="quarantine", help="Directory for rejected build evidence."
    )
    args = parser.parse_args()

    root = Path.cwd()
    files = iter_files([Path(path).resolve() for path in args.paths])
    findings = [finding for file_path in files for finding in scan_file(file_path, root)]

    if findings:
        write_quarantine(findings, Path(args.quarantine_dir))
        for finding in findings:
            print(
                f"{finding.path}:{finding.line_number}: {finding.rule}: {finding.evidence}",
                file=sys.stderr,
            )
        return 1

    print(f"Secret scan passed for {len(files)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
