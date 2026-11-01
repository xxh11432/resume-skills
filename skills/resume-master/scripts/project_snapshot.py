#!/usr/bin/env python3
"""Build a lightweight snapshot of a local project for resume material intake.

The snapshot is intentionally factual: it inventories files, languages, key
configuration files and git metadata. It does not judge project quality.

Usage:
    python scripts/project_snapshot.py --path <project-dir>
    python scripts/project_snapshot.py --path <project-dir> --out snapshot.md

Only the Python standard library is required.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable


EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "bower_components",
    "target",
    "build",
    "dist",
    "out",
    ".next",
    ".nuxt",
    ".output",
    ".svelte-kit",
    "coverage",
    "vendor",
    "bin",
    "obj",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".gradle",
    "logs",
    "tmp",
    "temp",
}

EXCLUDED_FILES = {
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "poetry.lock",
    "Pipfile.lock",
    "Cargo.lock",
    "go.sum",
    "composer.lock",
}

LANGUAGE_BY_EXT = {
    ".py": "Python",
    ".java": "Java",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".go": "Go",
    ".rs": "Rust",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".cs": "C#",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++",
    ".c": "C",
    ".h": "C",
    ".php": "PHP",
    ".rb": "Ruby",
    ".scala": "Scala",
    ".sql": "SQL",
    ".sh": "Shell",
    ".bash": "Shell",
    ".ps1": "PowerShell",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "CSS",
    ".less": "CSS",
    ".md": "Markdown",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".json": "JSON",
    ".xml": "XML",
}

SOURCE_LANGUAGES = {
    "Python",
    "Java",
    "Kotlin",
    "Go",
    "Rust",
    "TypeScript",
    "JavaScript",
    "Vue",
    "Svelte",
    "C#",
    "C++",
    "C",
    "PHP",
    "Ruby",
    "Scala",
    "SQL",
    "Shell",
    "PowerShell",
    "HTML",
    "CSS",
}

KEY_FILE_NAMES = {
    "readme.md",
    "readme.rst",
    "readme.txt",
    "package.json",
    "pnpm-workspace.yaml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "settings.gradle.kts",
    "pyproject.toml",
    "requirements.txt",
    "pipfile",
    "go.mod",
    "cargo.toml",
    "composer.json",
    "gemfile",
    "makefile",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    ".env.example",
    "application.yml",
    "application.yaml",
    "application.properties",
    "next.config.js",
    "next.config.mjs",
    "next.config.ts",
    "vite.config.js",
    "vite.config.ts",
    "nuxt.config.ts",
    "svelte.config.js",
    "tsconfig.json",
    "eslint.config.js",
    "eslint.config.mjs",
    ".eslintrc",
    ".eslintrc.json",
    "schema.prisma",
    "alembic.ini",
    "nginx.conf",
    "manage.py",
}

KEY_PATH_HINTS = (
    "/.github/workflows/",
    "/docs/",
    "/doc/",
    "/sql/",
    "/migrations/",
    "/deploy/",
    "/scripts/",
)

MAX_TEXT_BYTES = 2 * 1024 * 1024


def _run_git(project: Path, args: list[str]) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(project), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def _iter_files(root: Path) -> Iterable[Path]:
    binary_extensions = {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".pdf",
        ".zip",
        ".gz",
        ".exe",
        ".dll",
        ".class",
        ".jar",
    }
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        dirnames[:] = sorted(
            name
            for name in dirnames
            if name.lower() not in EXCLUDED_DIRS and not name.startswith(".git")
        )
        for name in sorted(filenames):
            path = current / name
            if name.lower() in EXCLUDED_FILES:
                continue
            if path.is_symlink():
                continue
            if path.suffix.lower() in binary_extensions:
                continue
            yield path


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _count_lines(path: Path) -> int | None:
    try:
        if path.stat().st_size > MAX_TEXT_BYTES:
            return None
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return sum(1 for line in text.splitlines() if line.strip())


def _collect_git(project: Path) -> dict[str, str]:
    info: dict[str, str] = {}
    if _run_git(project, ["rev-parse", "--is-inside-work-tree"]) != "true":
        return info

    branch = _run_git(project, ["rev-parse", "--abbrev-ref", "HEAD"])
    if branch:
        info["分支"] = branch

    last = _run_git(project, ["log", "-1", "--format=%h%x09%ad%x09%s", "--date=short"])
    if last:
        info["最近提交"] = last.replace("\t", " · ")

    count = _run_git(project, ["rev-list", "--count", "HEAD"])
    if count:
        info["提交数"] = count

    contributors = _run_git(project, ["shortlog", "-sne", "--all"])
    if contributors:
        top = [line.strip() for line in contributors.splitlines() if line.strip()][:5]
        info["主要提交者"] = "；".join(top)

    remote = _run_git(project, ["remote", "get-url", "origin"])
    if remote:
        info["远程仓库"] = _sanitize_remote(remote)
    return info


def _sanitize_remote(remote: str) -> str:
    """Remove credentials that may be embedded in a remote URL."""
    sanitized = re.sub(r"https://[^/@]+@", "https://", remote)
    sanitized = re.sub(r"(?i)(token|access_token|password)=[^&]+", r"\1=***", sanitized)
    return sanitized


def _is_key_file(rel: str, name: str) -> bool:
    lower_name = name.lower()
    lower_rel = rel.lower()
    if lower_name in KEY_FILE_NAMES:
        return True
    if lower_name.startswith("readme."):
        return True
    if any(hint in lower_rel for hint in KEY_PATH_HINTS):
        return True
    if lower_name.startswith("application."):
        return True
    if lower_name.startswith("dockerfile"):
        return True
    return False


def _collect(project: Path) -> dict[str, object]:
    files = list(_iter_files(project))
    language_files: dict[str, int] = {}
    language_lines: dict[str, int] = {}
    source_files = 0
    source_lines = 0
    text_files = 0
    test_files = 0
    todo_count = 0

    top_dirs: dict[str, int] = {}
    key_files: list[tuple[str, int | None, int | None]] = []
    largest: list[tuple[str, str, int]] = []

    for path in files:
        rel = _relative(path, project)
        name = path.name
        top = rel.split("/", 1)[0] if "/" in rel else "(根目录)"
        top_dirs[top] = top_dirs.get(top, 0) + 1

        suffix = path.suffix.lower()
        language = LANGUAGE_BY_EXT.get(suffix)
        if language:
            text_files += 1
            line_count = _count_lines(path)
            language_files[language] = language_files.get(language, 0) + 1
            if line_count is not None:
                language_lines[language] = language_lines.get(language, 0) + line_count
                if language in SOURCE_LANGUAGES:
                    source_files += 1
                    source_lines += line_count
                    largest.append((rel, language, line_count))
                    if "test" in rel.lower() or "spec" in rel.lower():
                        test_files += 1
                try:
                    if path.stat().st_size <= MAX_TEXT_BYTES:
                        content = path.read_text(encoding="utf-8", errors="ignore")
                        todo_count += content.upper().count("TODO") + content.upper().count("FIXME")
                except OSError:
                    pass

        if _is_key_file(rel, name):
            key_files.append((rel, path.stat().st_size, _count_lines(path)))

    key_files.sort(key=lambda item: (item[0].count("/"), item[0].lower()))
    largest.sort(key=lambda item: item[2], reverse=True)

    return {
        "files_scanned": len(files),
        "text_files": text_files,
        "source_files": source_files,
        "source_lines": source_lines,
        "test_files": test_files,
        "todo_count": todo_count,
        "language_files": language_files,
        "language_lines": language_lines,
        "top_dirs": top_dirs,
        "key_files": key_files[:80],
        "largest": largest[:15],
        "git": _collect_git(project),
    }


def _size_label(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / 1024 / 1024:.1f} MB"


def _render(project: Path, data: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append(f"# 项目快照：{project.name}")
    lines.append("")
    lines.append(f"- 路径：`{project}`")
    lines.append(f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"- 扫描文件数：{data['files_scanned']}（源码 {data['source_files']}，源码非空行约 {data['source_lines']}）")
    lines.append(f"- 测试相关文件：{data['test_files']}；TODO/FIXME 标记：{data['todo_count']}")
    lines.append("")

    git = data["git"]
    lines.append("## Git 信息")
    lines.append("")
    if git:
        for key, value in git.items():
            lines.append(f"- {key}：{value}")
    else:
        lines.append("- 未检测到 git 仓库，或 git 不可用。")
    lines.append("")

    lines.append("## 语言分布")
    lines.append("")
    lines.append("| 语言 | 文件数 | 非空行 |")
    lines.append("|---|---:|---:|")
    language_files = data["language_files"]
    language_lines = data["language_lines"]
    if language_files:
        for language, file_count in sorted(language_files.items(), key=lambda item: language_lines.get(item[0], 0), reverse=True):
            lines.append(f"| {language} | {file_count} | {language_lines.get(language, 0)} |")
    else:
        lines.append("| 未识别 | 0 | 0 |")
    lines.append("")

    lines.append("## 顶层目录")
    lines.append("")
    top_dirs = data["top_dirs"]
    if top_dirs:
        lines.append("| 目录 | 文件数 |")
        lines.append("|---|---:|")
        for name, count in sorted(top_dirs.items(), key=lambda item: item[1], reverse=True)[:25]:
            lines.append(f"| {name} | {count} |")
    else:
        lines.append("无。")
    lines.append("")

    lines.append("## 关键文件")
    lines.append("")
    key_files = data["key_files"]
    if key_files:
        lines.append("| 文件 | 大小 | 非空行 |")
        lines.append("|---|---:|---:|")
        for rel, size, line_count in key_files:
            line_label = "-" if line_count is None else str(line_count)
            lines.append(f"| `{rel}` | {_size_label(size)} | {line_label} |")
    else:
        lines.append("未发现常见的关键文件。")
    lines.append("")

    lines.append("## 最大的源码文件")
    lines.append("")
    largest = data["largest"]
    if largest:
        lines.append("| 文件 | 语言 | 非空行 |")
        lines.append("|---|---|---:|")
        for rel, language, line_count in largest:
            lines.append(f"| `{rel}` | {language} | {line_count} |")
    else:
        lines.append("未识别到源码文件。")
    lines.append("")

    lines.append("## 使用提示")
    lines.append("")
    lines.append("- 这份快照只负责盘点，不判断项目好坏，也不代表个人贡献。")
    lines.append("- 下一步优先读 README、依赖清单、入口文件、核心模块、部署与监控配置。")
    lines.append("- 任何数字、职责和技术选型理由，都需要代码、文档或用户确认作为证据。")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Create a factual snapshot of a local project.")
    parser.add_argument("--path", required=True, help="Project root directory")
    parser.add_argument("--out", default="", help="Write markdown to this path instead of stdout")
    args = parser.parse_args(argv)

    project = Path(args.path).expanduser().resolve()
    if not project.exists():
        print(f"[project_snapshot.py] ERROR: path not found: {project}", file=sys.stderr)
        return 2
    if not project.is_dir():
        print(f"[project_snapshot.py] ERROR: not a directory: {project}", file=sys.stderr)
        return 2

    markdown = _render(project, _collect(project))
    if args.out:
        out_path = Path(args.out).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(markdown, encoding="utf-8")
        print(str(out_path))
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
