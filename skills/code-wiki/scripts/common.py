"""Shared constants and low-level utilities for the code-wiki helper."""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

VERSION = "0.4.0"

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    ".next",
    ".nuxt",
    ".turbo",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "build",
    "code-wiki",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
}

MANIFEST_NAMES = {
    "AGENTS.md",
    "BUILD",
    "BUILD.bazel",
    "Cargo.toml",
    "CMakeLists.txt",
    "Gemfile",
    "Makefile.am",
    "Makefile.in",
    "Package.swift",
    "Podfile",
    "README.md",
    "WORKSPACE",
    "WORKSPACE.bazel",
    "bun.lockb",
    "composer.json",
    "configure",
    "configure.ac",
    "deno.json",
    "docker-compose.yml",
    "go.mod",
    "gradle.properties",
    "package-lock.json",
    "package.json",
    "pnpm-lock.yaml",
    "pyproject.toml",
    "requirements.txt",
    "setup.cfg",
    "setup.py",
    "meson.build",
    "meson_options.txt",
    "tsconfig.json",
    "uv.lock",
    "yarn.lock",
}

DOC_NAMES = {
    "AGENTS.md",
    "CHANGELOG.md",
    "COPYING",
    "CONTRIBUTING.md",
    "LICENSE",
    "LICENSE.md",
    "LICENSE.txt",
    "NOTICE",
    "NOTICE.md",
    "NOTICE.txt",
    "README.md",
    "SECURITY.md",
}

SOURCE_DIR_NAMES = {
    "app",
    "apps",
    "cmd",
    "components",
    "internal",
    "lib",
    "packages",
    "pkg",
    "server",
    "source",
    "src",
    "sources",
}

TEST_DIR_NAMES = {
    "__tests__",
    "features",
    "spec",
    "specs",
    "test",
    "tests",
}

INTERFACE_DIR_NAMES = {
    "api",
    "apis",
    "header",
    "headers",
    "include",
    "includes",
    "public",
}

ENTRYPOINT_NAMES = {
    "app.go",
    "app.py",
    "app.ts",
    "app.tsx",
    "cli.py",
    "index.js",
    "index.ts",
    "index.tsx",
    "main.go",
    "main.py",
    "main.rs",
    "main.swift",
    "main.ts",
    "main.tsx",
    "server.js",
    "server.py",
    "server.ts",
}

NOISY_SOURCE_PARTS = {
    ".github",
    "__tests__",
    "bench",
    "benches",
    "benchmark",
    "benchmarks",
    "benchsuite",
    "deps",
    "dist",
    "docs",
    "documentation",
    "example",
    "examples",
    "fixture",
    "fixtures",
    "playground",
    "playgrounds",
    "sample",
    "samples",
    "spec",
    "specs",
    "template",
    "templates",
    "testdata",
    "tests",
    "vendor",
}

VENDORED_ROOT_PARTS = {
    "deps",
    "third_party",
    "vendor",
}

OPS_ROOT_PARTS = {
    ".buildkite",
    ".circleci",
    ".github",
    ".gitlab",
    ".gitlab-ci.yml",
    ".readthedocs.yaml",
    "ci",
}

GENERATED_DOC_PARTS = {
    "classes",
    "docsets",
    "enums",
    "extensions",
    "protocols",
    "structs",
}

CODE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".h",
    ".hpp",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".m",
    ".mm",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
}

INTERFACE_EXTENSIONS = {
    ".h",
    ".hh",
    ".hpp",
    ".hxx",
    ".idl",
    ".modulemap",
}

EXT_LANGUAGE = {
    ".c": "C",
    ".cc": "C++",
    ".cpp": "C++",
    ".cs": "C#",
    ".css": "CSS",
    ".go": "Go",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".html": "HTML",
    ".java": "Java",
    ".js": "JavaScript",
    ".json": "JSON",
    ".jsx": "JavaScript React",
    ".kt": "Kotlin",
    ".m": "Objective-C",
    ".md": "Markdown",
    ".mm": "Objective-C++",
    ".php": "PHP",
    ".py": "Python",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".sh": "Shell",
    ".sql": "SQL",
    ".swift": "Swift",
    ".toml": "TOML",
    ".ts": "TypeScript",
    ".tsx": "TypeScript React",
    ".vue": "Vue",
    ".xml": "XML",
    ".yaml": "YAML",
    ".yml": "YAML",
}

REQUIRED_PAGES = [
    "index.html",
    "pages/project-context.html",
    "pages/overview.html",
    "pages/public-interfaces.html",
    "pages/architecture.html",
    "pages/runtime-state.html",
    "pages/dependencies.html",
    "pages/code-patterns.html",
    "pages/flows-basic.html",
    "pages/flows-advanced.html",
    "pages/testing-and-ops.html",
    "pages/change-guide.html",
    "pages/source-map.html",
    "pages/deep-dives/index.html",
]

NAV_ITEMS = [
    ("index", "Home", "index.html"),
    ("project-context", "Project Context", "pages/project-context.html"),
    ("overview", "Overview", "pages/overview.html"),
    ("public-interfaces", "Public Interfaces", "pages/public-interfaces.html"),
    ("architecture", "Architecture", "pages/architecture.html"),
    ("runtime-state", "Runtime State", "pages/runtime-state.html"),
    ("dependencies", "Dependencies & Build", "pages/dependencies.html"),
    ("code-patterns", "Code Patterns", "pages/code-patterns.html"),
    ("flows-basic", "Key Flows", "pages/flows-basic.html"),
    ("flows-advanced", "Advanced Behavior", "pages/flows-advanced.html"),
    ("testing-and-ops", "Testing & Ops", "pages/testing-and-ops.html"),
    ("change-guide", "Change Guide", "pages/change-guide.html"),
    ("source-map", "Source Map", "pages/source-map.html"),
    ("deep-dives", "Deep Dives", "pages/deep-dives/index.html"),
]

DEEP_DIVE_INDEX = "pages/deep-dives/index.html"
LARGE_REPO_FILE_THRESHOLD = 1000
LARGE_REPO_ROOT_THRESHOLD = 6
MIN_LARGE_REPO_DEEP_DIVES = 2
MAX_REVIEW_GRADE_EVIDENCE_RANGE = 120

GOVERNANCE_DOC_NAMES = {
    "authors",
    "changelog",
    "codeowners",
    "contributing",
    "copying",
    "license",
    "licence",
    "maintainers",
    "notice",
    "releases",
    "security",
    "support",
}

PLACEHOLDER_MARKERS = (
    "What to Fill In",
    "Replace this placeholder",
)

GENERIC_PROSE_PATTERNS = (
    r"\ba good onboarding wiki\b",
    r"\ba useful wiki\b",
    r"\bthis page should\b",
    r"\bthe page should\b",
    r"\bshould help a developer\b",
    r"\bshould be read as\b",
    r"\bit is still too thin\b",
    r"\blanguage-neutral terms\b",
    r"\bscalable across languages\b",
    r"\bif the flow cannot identify\b",
)

COMPREHENSION_PAGE_RULES = {
    "pages/project-context.html": {
        "min_words": 300,
        "min_sections": 3,
        "min_evidence": 2,
        "min_evidence_links": 5,
        "patterns": (
            r"\buse case\b|\bcapabilit|\bproduct\b|\bstakeholder\b|\baudience\b",
            r"\badoption\b|\bconstraint\b|\blicen[cs]e\b|\bsecurity\b|\bsupport\b|\bgovernance\b",
            r"\bofficial\b|\bupstream\b|\bdocs?\b|\bwhere to go\b|\bnext\b",
        ),
    },
    "pages/overview.html": {
        "min_words": 250,
        "min_sections": 3,
        "min_evidence": 2,
        "min_evidence_links": 5,
        "patterns": (
            r"\bscope\b|\bmental model\b",
            r"\bboundar|\bown(?:s|ed|ership)?\b|\bexternal\b|\bout of scope\b",
            r"\buse(?:d|s|r)?\b|\bconsumer\b|\bcaller\b|\bentrypoint\b|\bexample\b",
        ),
    },
    "pages/public-interfaces.html": {
        "min_words": 360,
        "min_sections": 4,
        "min_evidence": 3,
        "min_evidence_links": 8,
        "patterns": (
            r"\bpublic\b|\bAPI\b|\binterface\b|\bheader\b|\broute\b|\bcommand\b|\bexport",
            r"\bstable\b|\bextension\b|\binternal\b|\bincidental\b|\bcontract\b",
            r"\busage\b|\bconsumer\b|\bcaller\b|\bbinding\b|\bentrypoint\b|\bsample\b",
        ),
    },
    "pages/architecture.html": {
        "min_words": 425,
        "min_sections": 3,
        "min_evidence": 2,
        "min_evidence_links": 8,
        "patterns": (
            r"\bcomponent\b|\bmodule\b|\bsubsystem\b|\bboundar",
            r"\binteract|\bcollaborat|\bcall path\b|\blifecycle\b|\bsequence\b",
            r"\bclass\b|\bstruct\b|\bprotocol\b|\btrait\b|\binterface\b|\bfunction\b|\btype\b",
            r"\bcreate[sd]?\b|\bcall(?:s|ed)?\b|\bown(?:s|ed)?\b|\bmutat(?:e|es|ed)\b|\bregister",
        ),
    },
    "pages/runtime-state.html": {
        "min_words": 350,
        "min_sections": 3,
        "min_evidence": 2,
        "min_evidence_links": 6,
        "patterns": (
            r"\bstate\b|\blifecycle\b|\bcontext\b|\bsession\b|\bhandle\b|\bstorage\b",
            r"\bcreate[sd]?\b|\bmutat(?:e|es|ed)\b|\bown(?:s|ed)?\b|\bregister|\bcleanup\b",
            r"\bthread\b|\block\b|\basync\b|\bcallback\b|\bworker\b|\bconcurrency\b|\bcache\b",
        ),
    },
    "pages/dependencies.html": {
        "min_words": 220,
        "min_sections": 2,
        "min_evidence": 2,
        "min_evidence_links": 5,
        "patterns": (
            r"\bdependency\b|\bdependencies\b|\bmanifest\b|\bbuild\b",
            r"\bruntime\b|\bboundar|\btarget\b|\bpackage\b|\bprovider\b",
        ),
    },
    "pages/code-patterns.html": {
        "min_words": 300,
        "min_sections": 3,
        "min_evidence": 2,
        "min_evidence_links": 6,
        "patterns": (
            r"\bpattern\b|\bconvention\b|\babstraction\b|\blayer\b",
            r"\bstate\b|\berror\b|\bconfiguration\b|\bextension\b|\bpublic API\b",
        ),
    },
    "pages/flows-basic.html": {
        "min_words": 330,
        "min_sections": 3,
        "min_evidence": 2,
        "min_evidence_links": 5,
        "patterns": (
            r"\bentry\b|\bhappy\b|\bbasic\b|\brequest\b|\bcommand\b|\bstartup\b|\bflow\b",
            r"\bstep\b|\bsequence\b|\blifecycle\b|\bcall path\b",
            r"\bcall(?:s|ed)?\b|\breturn(?:s|ed)?\b|\bstate\b|\bcallback\b|\bhandler\b|\boutput\b",
        ),
    },
    "pages/flows-advanced.html": {
        "min_words": 360,
        "min_sections": 3,
        "min_evidence": 2,
        "min_evidence_links": 6,
        "patterns": (
            r"\bfailure\b|\bedge\b|\bretry\b|\basync\b|\bbackground\b|\badvanced\b|\berror\b",
            r"\bstate\b|\bintegration\b|\bconcurrency\b|\bcache\b|\bstorage\b|\bcleanup\b",
            r"\bbranch\b|\bcondition\b|\bcancel|\babort|\btimeout|\boverload|\bshutdown\b|\bfallback\b",
        ),
    },
    "pages/testing-and-ops.html": {
        "min_words": 260,
        "min_sections": 2,
        "min_evidence": 2,
        "min_evidence_links": 5,
        "patterns": (
            r"\btest\b|\bvalidation\b|\bCI\b|\bworkflow\b",
            r"\boperat|\bdeploy|\bobservab|\brun command\b|\benvironment\b",
            r"\bchange\b|\bcommand\b|\bmatrix\b|\bpackage\b|\brelease\b|\blint\b",
        ),
    },
    "pages/change-guide.html": {
        "min_words": 360,
        "min_sections": 3,
        "min_evidence": 2,
        "min_evidence_links": 6,
        "patterns": (
            r"\bchange\b|\bmodify\b|\bextend\b|\bdebug\b|\badd\b|\bremove\b",
            r"\btest\b|\bvalidate\b|\bcommand\b|\bCI\b|\bcoverage\b|\bfixture\b",
            r"\brisk\b|\bcaveat\b|\bcollaborator\b|\bfirst file\b|\bstart with\b|\bstart in\b",
        ),
    },
    "pages/source-map.html": {
        "min_words": 260,
        "min_sections": 2,
        "min_evidence": 2,
        "min_evidence_links": 5,
        "patterns": (
            r"\bresponsibilit|\bownership\b|\bdirectory\b|\bfile\b|\bsource root\b",
            r"\bsource\b|\btest\b|\bdocs\b|\bexample\b|\bgenerated\b|\bthird[- ]party\b|\bvendor",
        ),
    },
    "pages/deep-dives/index.html": {
        "min_words": 220,
        "min_sections": 2,
        "min_evidence": 1,
        "min_evidence_links": 3,
        "patterns": (
            r"\bdeep dive\b|\bsubsystem\b|\bmodule\b|\bcomponent\b|\bsurface\b",
            r"\bread\b|\bentry\b|\bflow\b|\bstate\b|\bchange\b|\bdebug\b",
        ),
    },
}

DEEP_DIVE_PAGE_RULE = {
    "min_words": 350,
    "min_sections": 3,
    "min_evidence": 2,
    "min_evidence_links": 5,
    "patterns": (
        r"\bsubsystem\b|\bmodule\b|\bcomponent\b|\bsurface\b|\blayer\b",
        r"\bentry\b|\bcall\b|\bflow\b|\bstate\b|\bcallback\b|\blifecycle\b",
        r"\bchange\b|\btest\b|\brisk\b|\bdebug\b|\bextend\b|\bfailure\b",
    ),
}

GENERIC_DIAGRAM_EDGE_SETS = (
    frozenset({"owns", "feeds", "supports"}),
    frozenset({"calls", "returns", "extends"}),
    frozenset({"starts", "dispatches", "emits"}),
    frozenset({"branches", "recovers", "cleans"}),
    frozenset({"declares", "selects", "validates"}),
)

EVIDENCE_REF_RE = re.compile(r"^(?P<path>.+?):(?P<start>\d+)(?:-(?P<end>\d+))?$")
EVIDENCE_BLOCK_RE = re.compile(
    r"""<aside\b[^>]*class=["'][^"']*\bevidence\b[^"']*["'][^>]*>(?P<body>.*?)</aside>""",
    re.IGNORECASE | re.DOTALL,
)
ANCHOR_RE = re.compile(r"""<a\b(?P<attrs>[^>]*)>(?P<body>.*?)</a>""", re.IGNORECASE | re.DOTALL)
ATTR_RE = re.compile(r"""(?P<name>[\w:-]+)=["'](?P<value>[^"']+)["']""", re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_rel(path: Path) -> str:
    return path.as_posix()


def git_output(repo: Path, *args: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    output = completed.stdout.strip()
    return output or None


def normalize_github_web_url(remote_url: str | None) -> tuple[str | None, str | None]:
    if not remote_url:
        return None, None

    value = remote_url.strip()
    path: str | None = None

    if value.startswith("git@github.com:"):
        path = value.split(":", 1)[1]
    elif value.startswith("ssh://"):
        parsed = urlparse(value)
        if parsed.hostname and parsed.hostname.lower() == "github.com":
            path = parsed.path.lstrip("/")
    else:
        parsed = urlparse(value)
        if parsed.hostname and parsed.hostname.lower() in {"github.com", "www.github.com"}:
            path = parsed.path.lstrip("/")

    if not path:
        return None, None

    path = path.removesuffix(".git").strip("/")
    parts = [part for part in path.split("/") if part]
    if len(parts) < 2:
        return None, None

    return f"https://github.com/{parts[0]}/{parts[1]}", "github"


def git_metadata(repo: Path) -> dict[str, object]:
    inside = git_output(repo, "rev-parse", "--is-inside-work-tree") == "true"
    commit = git_output(repo, "rev-parse", "HEAD") if inside else None
    branch = git_output(repo, "rev-parse", "--abbrev-ref", "HEAD") if inside else None
    if branch == "HEAD":
        branch = None
    remote_url = git_output(repo, "config", "--get", "remote.origin.url") if inside else None
    web_url, host = normalize_github_web_url(remote_url)
    dirty = bool(git_output(repo, "status", "--short")) if inside else None

    return {
        "has_git_directory": (repo / ".git").exists(),
        "is_git_worktree": inside,
        "remote_url": remote_url,
        "web_url": web_url,
        "host": host,
        "commit": commit,
        "branch": branch,
        "dirty": dirty,
    }
