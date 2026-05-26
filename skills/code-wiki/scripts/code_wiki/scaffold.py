"""Static HTML wiki scaffolding for code-wiki."""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

from code_wiki.wiki_contract import NAV_ITEMS


def skill_root() -> Path:
    return Path(__file__).resolve().parents[2]


def page_title_from_slug(slug: str) -> str:
    return slug.replace("-", " ").title().replace("And", "and")


def rel_nav_target(prefix: str, href: str) -> str:
    return href if prefix == "" else f"{prefix}{href}"


def nav_html(prefix: str, active: str) -> str:
    links = []
    for slug, label, href in NAV_ITEMS:
        target = rel_nav_target(prefix, href)
        class_name = ' class="active"' if slug == active else ""
        links.append(f'<a{class_name} href="{html.escape(target)}">{html.escape(label)}</a>')
    return "\n".join(links)


def page_nav_html(prefix: str, active: str) -> str:
    active_index = next(
        (index for index, item in enumerate(NAV_ITEMS) if item[0] == active),
        None,
    )
    if active_index is None:
        return ""

    links = []
    for rel_index, direction in ((active_index - 1, "Previous"), (active_index + 1, "Next")):
        if rel_index < 0 or rel_index >= len(NAV_ITEMS):
            continue
        slug, label, href = NAV_ITEMS[rel_index]
        target = rel_nav_target(prefix, href)
        links.append(
            f'<a href="{html.escape(target)}"><span>{direction}</span><strong>{html.escape(label)}</strong></a>'
        )
    if not links:
        return ""
    return '    <nav class="page-nav" aria-label="Page navigation">\n      ' + "\n      ".join(links) + "\n    </nav>"


def render_page(title: str, body: str, prefix: str, active: str) -> str:
    css = f"{prefix}assets/style.css"
    js = f"{prefix}assets/app.js"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{css}">
</head>
<body>
  <aside class="sidebar">
    <div class="brand-row">
      <div class="brand">Code Wiki</div>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="wiki-nav">Menu</button>
    </div>
    <nav id="wiki-nav" class="site-nav">
{nav_html(prefix, active)}
    </nav>
  </aside>
  <main>
{body}
{page_nav_html(prefix, active)}
  </main>
  <script src="{js}"></script>
</body>
</html>
"""


def placeholder_body(title: str, description: str) -> str:
    return f"""    <header class="page-header">
      <p class="eyebrow">Evidence-backed repository guide</p>
      <h1>{html.escape(title)}</h1>
      <p class="lead">{html.escape(description)}</p>
      <div class="meta-bar">
        <span class="meta-pill">Claim-backed sections required</span>
        <span class="meta-pill">Deterministic diagrams first</span>
        <span class="meta-pill">Collapsible evidence expected</span>
      </div>
    </header>
    <section class="doc-section">
      <h2>What to Fill In</h2>
      <p>Replace this placeholder with ready claims from data/claim-matrix.json, source inspection, and subagent research. Keep every claim tied to file evidence.</p>
    </section>
"""


def copy_template_assets(out_dir: Path) -> None:
    template_dir = skill_root() / "assets" / "wiki-template"
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    required_assets = ("style.css", "app.js")
    missing_assets = [name for name in required_assets if not (template_dir / name).is_file()]
    if missing_assets:
        missing = ", ".join(missing_assets)
        raise SystemExit(f"missing required template asset(s) in {template_dir}: {missing}")

    for name in required_assets:
        source = template_dir / name
        destination = assets_dir / name
        shutil.copyfile(source, destination)


def init_local_source_cache(out_dir: Path) -> None:
    cache_dir = out_dir / ".cache"
    sources_dir = cache_dir / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / ".gitignore").write_text("*\n!.gitignore\n", encoding="utf-8")


def write_claim_matrix_example(out_dir: Path) -> None:
    example = {
        "schema_version": 1,
        "repo": {
            "name": "example-repo",
            "path": "/absolute/path/to/example-repo",
            "web_url": "https://github.com/example/example-repo",
            "commit": "0000000000000000000000000000000000000000",
            "dirty": False,
        },
        "inventory": {
            "path": "/absolute/path/to/wiki/data/inventory.json",
            "schema_version": 1,
            "counts": {"files": 0},
        },
        "page_targets": [
            {
                "page": "pages/overview.html",
                "min_ready_claims": 2,
                "status": "pending",
            }
        ],
        "deep_dive_targets": {
            "minimum_pages": 2,
            "min_ready_claims_per_page": 3,
            "status": "pending",
            "suggested_pages": [],
        },
        "coverage_roots": [
            {
                "root": "src",
                "kind": "source",
                "reason": "primary source root",
                "status": "pending",
                "not_applicable_reason": "",
            }
        ],
        "claims": [
            {
                "claim": "Replace with a concrete repo-specific statement.",
                "page": "pages/overview.html",
                "evidence": ["src/main.py:1-20"],
                "why_it_matters": "Explain how this changes a maintainer's mental model.",
                "status": "draft",
            }
        ],
    }
    (out_dir / "data" / "claim-matrix.example.json").write_text(
        json.dumps(example, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def scaffold(out_arg: str, title: str, local_source_cache: bool = False) -> None:
    out_dir = Path(out_arg).expanduser().resolve()
    (out_dir / "pages").mkdir(parents=True, exist_ok=True)
    (out_dir / "pages" / "deep-dives").mkdir(parents=True, exist_ok=True)
    (out_dir / "assets" / "diagrams").mkdir(parents=True, exist_ok=True)
    (out_dir / "assets" / "images").mkdir(parents=True, exist_ok=True)
    (out_dir / "data").mkdir(parents=True, exist_ok=True)
    copy_template_assets(out_dir)
    write_claim_matrix_example(out_dir)
    if local_source_cache:
        init_local_source_cache(out_dir)

    index_body = f"""    <header class="hero">
      <p class="eyebrow">Code Wiki</p>
      <h1>{html.escape(title)}</h1>
      <p class="lead">A linked repository guide for project context, architecture, public surfaces, dependencies, patterns, flows, tests, and operations.</p>
      <div class="meta-bar">
        <span class="meta-pill">Static HTML</span>
        <span class="meta-pill">Source-backed</span>
        <span class="meta-pill">Evidence-linked</span>
      </div>
    </header>
    <section class="grid">
      <a class="card" href="pages/project-context.html"><span>01</span><strong>Project Context</strong><p>Use cases, audience, adoption constraints, governance, and upstream docs.</p></a>
      <a class="card" href="pages/overview.html"><span>02</span><strong>Overview</strong><p>Scope, ownership boundaries, runtime shape, and mental model.</p></a>
      <a class="card" href="pages/public-interfaces.html"><span>03</span><strong>Public Interfaces</strong><p>Exported APIs, commands, headers, routes, bindings, and extension contracts.</p></a>
      <a class="card" href="pages/architecture.html"><span>04</span><strong>Architecture</strong><p>Modules, boundaries, interaction maps, and key collaborators.</p></a>
      <a class="card" href="pages/runtime-state.html"><span>05</span><strong>Runtime State</strong><p>State owners, lifecycles, concurrency, storage, and cleanup responsibilities.</p></a>
      <a class="card" href="pages/dependencies.html"><span>06</span><strong>Dependencies & Build</strong><p>Manifests, build/runtime tools, and dependency boundary impact.</p></a>
      <a class="card" href="pages/code-patterns.html"><span>07</span><strong>Code Patterns</strong><p>Conventions, layering, error handling, and extension patterns.</p></a>
      <a class="card" href="pages/flows-basic.html"><span>08</span><strong>Key Flows</strong><p>Primary entrypoint-to-collaborator happy paths.</p></a>
      <a class="card" href="pages/flows-advanced.html"><span>09</span><strong>Advanced Behavior</strong><p>State transitions, failure modes, async work, and cleanup.</p></a>
      <a class="card" href="pages/testing-and-ops.html"><span>10</span><strong>Testing & Ops</strong><p>Validation, CI, exact commands, deployment, and operator notes.</p></a>
      <a class="card" href="pages/change-guide.html"><span>11</span><strong>Change Guide</strong><p>Task recipes, compatibility risks, validation, and rollback paths.</p></a>
      <a class="card" href="pages/deep-dives/index.html"><span>12</span><strong>Deep Dives</strong><p>Repo-specific subsystem pages for large or multi-surface systems.</p></a>
      <a class="card" href="pages/source-map.html"><span>13</span><strong>Source Map</strong><p>Directory responsibilities, generated code, examples, tests, and vendor boundaries.</p></a>
    </section>
"""
    (out_dir / "index.html").write_text(
        render_page(title, index_body, "", "index"), encoding="utf-8"
    )

    page_specs = {
        "project-context": "Explain use cases, audience, product or stakeholder framing, adoption constraints, license/security/support signals, and official upstream docs.",
        "overview": "Explain repository scope, ownership boundaries, audience, runtime shape, and the shortest mental model for a new developer.",
        "public-interfaces": "Document exported APIs, commands, headers, routes, bindings, stable extension points, and one usage-shaped path through them.",
        "architecture": "Document modules, ownership boundaries, public APIs, component diagrams, and class/type/function interaction maps.",
        "runtime-state": "Explain state carriers, lifecycle ownership, concurrency, persistence, caches, handles, cleanup, and shutdown responsibilities.",
        "dependencies": "Explain dependency manifests, build tooling, runtime frameworks, and how dependencies shape repository boundaries.",
        "code-patterns": "Summarize naming, layering, state ownership, error handling, configuration, and extension conventions.",
        "flows-basic": "Walk through the main happy-path flows from entrypoint to collaborators with source evidence.",
        "flows-advanced": "Cover state transitions, edge cases, retries, async work, integrations, failure modes, and cleanup.",
        "testing-and-ops": "Explain tests, local run commands, CI, deployments, observability, environment, and operational caveats.",
        "change-guide": "Map common developer changes to first files, collaborators, tests, commands, and operational risks.",
        "source-map": "Map important directories and files to responsibilities, source/test/docs/example/vendor boundaries, and generated assets.",
    }
    for slug, description in page_specs.items():
        path = out_dir / "pages" / f"{slug}.html"
        title_text = page_title_from_slug(slug)
        path.write_text(
            render_page(title_text, placeholder_body(title_text, description), "../", slug),
            encoding="utf-8",
        )

    deep_dive_title = "Deep Dives"
    deep_dive_description = (
        "Index repo-specific subsystem pages. For large repos, create two to five "
        "leaf pages under pages/deep-dives/ and link them here with source-backed summaries."
    )
    (out_dir / "pages" / "deep-dives" / "index.html").write_text(
        render_page(
            deep_dive_title,
            placeholder_body(deep_dive_title, deep_dive_description),
            "../../",
            "deep-dives",
        ),
        encoding="utf-8",
    )

    print(f"scaffolded wiki at {out_dir}")
