#!/usr/bin/env python3
from __future__ import annotations

import re
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from pypdf import PdfReader  # type: ignore
except Exception:  # pragma: no cover
    PdfReader = None

REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
START_MARKER = "<!-- AUTO-GENERATED-SUMMARY:START -->"
END_MARKER = "<!-- AUTO-GENERATED-SUMMARY:END -->"

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".html",
    ".htm",
    ".php",
    ".js",
    ".ts",
    ".css",
    ".json",
    ".yml",
    ".yaml",
    ".xml",
    ".csv",
    ".sh",
}

TOPIC_PATTERNS = OrderedDict(
    [
        (
            "Cloud foundations and pricing",
            [
                r"\biaas\b",
                r"\bpaas\b",
                r"\bsaas\b",
                r"global infrastructure",
                r"free tier",
                r"deployment model",
            ],
        ),
        (
            "IAM fundamentals and account security",
            [
                r"\biam\b",
                r"least privilege",
                r"shared responsibility",
                r"multi\s*-?factor authentication",
                r"\bmfa\b",
            ],
        ),
        (
            "EC2 and compute concepts",
            [r"\bec2\b", r"instance type", r"\bami\b", r"elastic compute cloud"],
        ),
        (
            "VPC networking",
            [r"\bvpc\b", r"subnet", r"route table", r"internet gateway", r"security group"],
        ),
        (
            "Load balancing and auto scaling",
            [r"load balancer", r"\balb\b", r"target group", r"auto scaling", r"\basg\b"],
        ),
        (
            "S3 and storage architecture",
            [r"\bs3\b", r"storage class", r"lifecycle", r"versioning", r"\bebs\b", r"\befs\b"],
        ),
        (
            "AWS database services",
            [r"\brds\b", r"aurora", r"dynamodb", r"\bdatabase\b", r"mysql", r"postgresql"],
        ),
        (
            "Hands-on deployment labs",
            [r"\bdemo\b", r"\blab\b", r"apache", r"php", r"crud", r"student management", r"static website"],
        ),
    ]
)


@dataclass
class DaySummary:
    day_name: str
    summary: str
    artifacts: list[str]


def sorted_day_dirs() -> list[Path]:
    days = [p for p in REPO_ROOT.iterdir() if p.is_dir() and re.fullmatch(r"Day\s+\d+", p.name)]
    return sorted(days, key=lambda p: int(re.search(r"\d+", p.name).group()))


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def read_pdf_text(path: Path) -> str:
    if PdfReader is None:
        return ""
    try:
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:
        return ""


def collect_text(paths: Iterable[Path]) -> str:
    chunks: list[str] = []
    for path in paths:
        suffix = path.suffix.lower()
        if suffix in TEXT_EXTENSIONS:
            chunks.append(read_text_file(path))
        elif suffix == ".pdf":
            chunks.append(read_pdf_text(path))
    return "\n".join(chunks).lower()


def detect_topics(text: str) -> list[str]:
    matched: list[str] = []
    for topic, patterns in TOPIC_PATTERNS.items():
        score = sum(1 for pattern in patterns if re.search(pattern, text))
        if score >= 1:
            matched.append(topic)
    return matched


def infer_summary(files: list[Path]) -> str:
    topics = detect_topics(collect_text(files))
    if topics:
        if len(topics) == 1:
            return topics[0]
        if len(topics) == 2:
            return f"{topics[0]} and {topics[1]}"
        return ", ".join(topics[:2]) + f", and {topics[2]}"

    if any(path.suffix.lower() == ".pdf" for path in files):
        return "AWS training notes and reference materials"

    return "Hands-on notes and learning artifacts"


def pick_artifacts(day_dir: Path) -> list[str]:
    files = [p for p in day_dir.rglob("*") if p.is_file()]
    if not files:
        return []

    def priority(path: Path) -> tuple[int, int, str]:
        ext = path.suffix.lower()
        if ext in {".md", ".pdf"}:
            level = 0
        elif ext in {".html", ".php", ".sql", ".js", ".ts", ".py"}:
            level = 1
        else:
            level = 2
        rel = path.relative_to(REPO_ROOT)
        depth = len(rel.parts)
        return (level, depth, rel.as_posix().lower())

    selected = sorted(files, key=priority)[:4]
    return [f"`{p.relative_to(REPO_ROOT).as_posix()}`" for p in selected]


def extract_existing_summaries(readme: str) -> dict[str, str]:
    summaries: dict[str, str] = {}
    for line in readme.splitlines():
        match = re.match(r"^\|\s*(Day\s+\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$", line)
        if not match:
            continue
        day_name, summary, _ = match.groups()
        if day_name not in summaries:
            summaries[day_name] = summary
    return summaries


def build_table_block(summaries: list[DaySummary]) -> str:
    lines = [
        START_MARKER,
        "| Day | Coverage Summary | Main Artifacts |",
        "| --- | --- | --- |",
    ]
    for day in summaries:
        artifacts = ", ".join(day.artifacts) if day.artifacts else "-"
        lines.append(f"| {day.day_name} | {day.summary} | {artifacts} |")
    lines.append(END_MARKER)
    return "\n".join(lines)


def replace_existing_table_section(readme: str, block: str) -> str:
    heading_pattern = re.compile(r"^##\s+Day-by-Day Coverage\s*$", re.MULTILINE)
    heading_match = heading_pattern.search(readme)
    if not heading_match:
        return readme.rstrip() + "\n\n## Day-by-Day Coverage\n\n" + block + "\n"

    heading_end = heading_match.end()
    after_heading = readme[heading_end:]

    table_header_match = re.search(r"^\|\s*Day\s*\|.*$", after_heading, flags=re.MULTILINE)
    if not table_header_match:
        insert_at = heading_end
        return readme[:insert_at] + "\n\n" + block + readme[insert_at:]

    table_start = table_header_match.start()
    table_tail = after_heading[table_start:]
    table_end_match = re.search(r"\n(?!\|)", table_tail)
    table_end = table_start + (table_end_match.start() + 1 if table_end_match else len(table_tail))

    start = heading_end + table_start
    end = heading_end + table_end
    return readme[:start] + block + "\n" + readme[end:]


def update_readme() -> None:
    if not README_PATH.exists():
        raise FileNotFoundError(f"README not found: {README_PATH}")

    readme = README_PATH.read_text(encoding="utf-8")
    existing_summaries = extract_existing_summaries(readme)

    day_summaries: list[DaySummary] = []
    for day_dir in sorted_day_dirs():
        files = [p for p in day_dir.rglob("*") if p.is_file()]
        day_summaries.append(
            DaySummary(
                day_name=day_dir.name,
                summary=existing_summaries.get(day_dir.name, infer_summary(files)),
                artifacts=pick_artifacts(day_dir),
            )
        )

    block = build_table_block(day_summaries)

    if START_MARKER in readme and END_MARKER in readme:
        pattern = re.compile(rf"{re.escape(START_MARKER)}[\s\S]*?{re.escape(END_MARKER)}", re.MULTILINE)
        updated = pattern.sub(block, readme, count=1)
    else:
        updated = replace_existing_table_section(readme, block)

    README_PATH.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    update_readme()
