#!/usr/bin/env python3
"""Import skills from .agents/skills/ (skills.sh format) into skill_mcp/skills_data/ (skills-mcp format).

Reads each SKILL.md, preserves the body, and enriches the frontmatter to match
the skills-mcp schema expected by the seed script.

Usage:
    python scripts/import_skills.py [--dry-run] [--only SLUG1,SLUG2,...]
"""
import argparse
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install PyYAML")

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / ".agents" / "skills"
TARGET_DIR = ROOT / "skill_mcp" / "skills_data"

EXISTING_SKILLS = {p.name for p in TARGET_DIR.iterdir() if p.is_dir() and (p / "SKILL.md").exists()}

TODAY = date.today().isoformat()

# Skills to skip (already exist in skills_data or are meta/template skills)
SKIP_SKILLS = EXISTING_SKILLS | {
    "template-skill",
    "skill-creator",
    "skill-improver",
    "find-skills",
    "using-superpowers",
    "let-fate-decide",
    # Overlap with existing skills (different slug, same content)
    "pdf",          # we have pdf-processing
    "docx",         # we have docx-creator
    "xlsx",         # we have xlsx-creator
    "pptx",         # we have pptx-creator
    "claude-api",   # we have claude-api
    "mcp-builder",  # we have mcp-server-builder
    "web-artifacts-builder",  # we have web-artifacts-builder
    "frontend-design",        # we have frontend-design
    "react-patterns",         # we have react-best-practices
    "vercel-react-best-practices",  # we have react-best-practices
}

# Category and metadata inference from skill slug patterns
CATEGORY_PATTERNS = {
    "laravel": {"tags": ["laravel", "php", "backend", "web-framework"], "author": "Laravel Community", "complexity": "intermediate", "prereqs": ["PHP 8.1+", "Composer", "Laravel 11+"]},
    "expo": {"tags": ["expo", "react-native", "mobile", "javascript"], "author": "Expo", "complexity": "intermediate", "prereqs": ["Node.js 18+", "Expo CLI", "React Native knowledge"]},
    "prisma": {"tags": ["prisma", "orm", "database", "typescript"], "author": "Prisma", "complexity": "intermediate", "prereqs": ["Node.js 18+", "TypeScript", "SQL basics"]},
    "neo4j": {"tags": ["neo4j", "graph-database", "cypher", "database"], "author": "Neo4j", "complexity": "intermediate", "prereqs": ["Neo4j 2025+", "Graph database concepts"]},
    "clerk": {"tags": ["clerk", "authentication", "nextjs", "security"], "author": "Clerk", "complexity": "intermediate", "prereqs": ["Next.js 14+", "React", "Clerk account"]},
    "azure": {"tags": ["azure", "cloud", "microsoft", "infrastructure"], "author": "Microsoft", "complexity": "intermediate", "prereqs": ["Azure account", "Azure CLI"]},
    "supabase": {"tags": ["supabase", "postgresql", "backend", "auth"], "author": "Supabase", "complexity": "intermediate", "prereqs": ["Supabase account", "SQL basics"]},
    "vercel": {"tags": ["vercel", "deployment", "react", "nextjs"], "author": "Vercel", "complexity": "intermediate", "prereqs": ["Node.js 18+", "React/Next.js"]},
    "next": {"tags": ["nextjs", "react", "frontend", "ssr"], "author": "Vercel", "complexity": "intermediate", "prereqs": ["Node.js 18+", "React", "Next.js 14+"]},
    "tailwind": {"tags": ["tailwind", "css", "frontend", "design"], "author": "Community", "complexity": "beginner", "prereqs": ["HTML/CSS basics", "Tailwind CSS 4+"]},
    "wordpress": {"tags": ["wordpress", "cms", "php", "web"], "author": "Community", "complexity": "beginner", "prereqs": ["WordPress installation", "PHP basics"]},
    "shopify": {"tags": ["shopify", "ecommerce", "liquid", "web"], "author": "Community", "complexity": "intermediate", "prereqs": ["Shopify account", "Liquid templating"]},
    "solana": {"tags": ["solana", "blockchain", "web3", "rust"], "author": "Solana Foundation", "complexity": "advanced", "prereqs": ["Rust", "Node.js 18+", "Solana CLI"]},
}

SECURITY_SKILLS = {
    "codeql", "semgrep", "semgrep-rule-creator", "semgrep-rule-variant-creator",
    "variant-analysis", "differential-review", "insecure-defaults",
    "firebase-apk-scanner", "supply-chain-risk-auditor", "zeroize-audit",
    "constant-time-analysis", "constant-time-testing", "yara-rule-authoring",
    "audit-security", "audit-augmentation", "audit-context-building",
    "audit-prep-assistant", "address-sanitizer", "coverage-analysis",
    "mutation-testing", "property-based-testing", "fp-check",
    "cargo-fuzz", "aflpp", "libfuzzer", "libafl", "ruzzy", "ossfuzz",
    "atheris", "wycheproof", "fuzzing-dictionary", "fuzzing-obstacles",
    "harness-writing", "seatbelt-sandboxer", "token-integration-analyzer",
    "mermaid-to-proverif", "crypto-protocol-diagram", "sarif-parsing",
    "burpsuite-project-parser", "trailmark", "trailmark-structural",
    "trailmark-summary", "algorand-vulnerability-scanner",
    "cairo-vulnerability-scanner", "cosmos-vulnerability-scanner",
    "solana-vulnerability-scanner", "substrate-vulnerability-scanner",
    "ton-vulnerability-scanner", "entry-point-analyzer",
    "sharp-edges", "genotoxic", "dimensional-analysis",
    "spec-to-code-compliance", "secure-workflow-guide",
}


def infer_category(slug: str) -> dict:
    """Infer metadata from slug patterns."""
    for pattern, meta in CATEGORY_PATTERNS.items():
        if pattern in slug:
            return meta.copy()
    if slug in SECURITY_SKILLS:
        return {
            "tags": ["security", "audit", "vulnerability", "devsecops"],
            "author": "Trail of Bits",
            "complexity": "advanced",
            "prereqs": ["Security fundamentals", "CLI tools"],
        }
    return {
        "tags": ["agent-skill", "automation"],
        "author": "Community",
        "complexity": "intermediate",
        "prereqs": [],
    }


def extract_triggers(slug: str, description: str, body: str) -> list[str]:
    """Generate trigger phrases from the skill slug and description."""
    triggers = []
    words = slug.replace("-", " ")
    triggers.append(words)

    if description:
        # Extract key action phrases from description
        desc_lower = description.lower()
        for pattern in [
            r"use when (?:the user )?(?:is |asks? to )?([\w\s,]+?)(?:\.|,|$)",
            r"helps? (?:with |you )?([\w\s,]+?)(?:\.|,|$)",
            r"triggers? on [\"']?([\w\s,]+?)[\"']?(?:\.|,|$)",
        ]:
            matches = re.findall(pattern, desc_lower)
            for m in matches:
                parts = [p.strip() for p in m.split(",") if len(p.strip()) > 3]
                triggers.extend(parts[:5])

    # Deduplicate and limit
    seen = set()
    unique = []
    for t in triggers:
        t = t.strip()[:120]
        if t and t.lower() not in seen and len(t) > 3:
            seen.add(t.lower())
            unique.append(t)
    return unique[:10] or [words]


def extract_use_cases(description: str, slug: str) -> list[str]:
    """Generate use cases from description."""
    cases = []
    words = slug.replace("-", " ").title()
    if description:
        cases.append(f"Apply {words} best practices in projects")
    cases.append(f"Get guidance on {words} implementation")
    cases.append(f"Follow {words} patterns and conventions")
    return cases[:5]


def parse_skill(skill_dir: Path) -> dict | None:
    """Parse a skills.sh SKILL.md and return enriched metadata."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None

    text = skill_md.read_text(encoding="utf-8", errors="replace")

    # Parse frontmatter
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None

    try:
        fm = yaml.safe_load(text[3:end]) or {}
    except Exception:
        return None

    body = text[end + 4:].strip()
    if not body:
        return None

    slug = skill_dir.name
    name = fm.get("name", slug)
    description = fm.get("description", "")
    if isinstance(description, dict):
        description = str(description)
    description = description.strip()

    # Truncate description to 220 chars
    if len(description) > 220:
        description = description[:217] + "..."
    if len(description) < 50:
        description = f"{name.replace('-', ' ').title()} - {description}".ljust(50)[:220]

    # Get existing metadata if present
    src_meta = fm.get("metadata", {}) or {}
    author = src_meta.get("author", fm.get("author", ""))
    version = src_meta.get("version", fm.get("version", "1.0"))
    license_val = fm.get("license", "MIT")

    # Infer category metadata
    cat = infer_category(slug)
    if not author:
        author = cat.get("author", "Community")

    tags = src_meta.get("tags", cat.get("tags", ["agent-skill"]))
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]

    platforms = src_meta.get("platforms", ["claude-code", "cursor", "windsurf", "any"])
    triggers = src_meta.get("triggers") or extract_triggers(slug, description, body)
    use_cases = src_meta.get("use_cases") or extract_use_cases(description, slug)
    complexity = src_meta.get("complexity_level", cat.get("complexity", "intermediate"))
    prereqs = src_meta.get("prerequisites", cat.get("prereqs", []))
    estimated_time = src_meta.get("estimated_time", "15-25 minutes")

    # Determine source URL
    source_url = src_meta.get("source_url", f"https://skills.sh/{slug}")

    # Check for tier-3 assets
    has_refs = any((skill_dir / d).exists() and any((skill_dir / d).iterdir())
                   for d in ("references", "docs", "ref"))
    has_scripts = any((skill_dir / d).exists() and any((skill_dir / d).iterdir())
                      for d in ("scripts",))
    has_assets = any((skill_dir / d).exists() and any((skill_dir / d).iterdir())
                     for d in ("assets", "examples", "templates"))
    has_tier3 = has_refs or has_scripts or has_assets

    return {
        "slug": slug,
        "name": name,
        "description": description,
        "license": license_val,
        "author": author,
        "version": str(version),
        "tags": tags,
        "platforms": platforms,
        "triggers": triggers,
        "use_cases": use_cases,
        "estimated_time": estimated_time,
        "complexity_level": complexity,
        "prerequisites": prereqs if prereqs else ["Basic programming knowledge"],
        "source_url": source_url,
        "last_updated": TODAY,
        "has_tier3": has_tier3,
        "body": body,
        "source_dir": skill_dir,
        "has_scripts": has_scripts,
        "has_assets": has_assets,
        "has_refs": has_refs,
    }


def build_skill_md(skill: dict) -> str:
    """Build a skills-mcp format SKILL.md."""
    fm = {
        "name": skill["slug"],
        "description": skill["description"],
        "license": skill["license"],
        "metadata": {
            "author": skill["author"],
            "version": skill["version"],
            "tags": skill["tags"],
            "platforms": skill["platforms"],
            "triggers": skill["triggers"],
            "use_cases": skill["use_cases"],
            "estimated_time": skill["estimated_time"],
            "complexity_level": skill["complexity_level"],
            "prerequisites": skill["prerequisites"],
            "source_url": skill["source_url"],
            "last_updated": skill["last_updated"],
            "has_tier3": skill["has_tier3"],
        },
    }
    frontmatter = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False, width=200)
    return f"---\n{frontmatter}---\n\n{skill['body']}\n"


def copy_tier3(skill: dict, target: Path):
    """Copy tier-3 assets from source to target directory."""
    src = skill["source_dir"]

    # Map source dirs to target dirs
    mappings = [
        (["references", "docs", "ref"], "references"),
        (["scripts"], "scripts"),
        (["assets", "examples", "templates"], "assets"),
    ]

    for src_names, tgt_name in mappings:
        tgt_dir = target / tgt_name
        tgt_dir.mkdir(exist_ok=True)
        for src_name in src_names:
            src_dir = src / src_name
            if src_dir.is_dir():
                for f in src_dir.iterdir():
                    if f.is_file() and f.name != ".gitkeep":
                        shutil.copy2(f, tgt_dir / f.name)

    # Ensure .gitkeep in empty dirs
    for sub in ("references", "scripts", "assets"):
        d = target / sub
        d.mkdir(exist_ok=True)
        gk = d / ".gitkeep"
        if not gk.exists():
            gk.touch()


def main():
    parser = argparse.ArgumentParser(description="Import skills.sh skills into skills-mcp format")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be done without writing")
    parser.add_argument("--only", type=str, help="Comma-separated list of skill slugs to import")
    args = parser.parse_args()

    if not SOURCE_DIR.is_dir():
        sys.exit(f"Source directory not found: {SOURCE_DIR}")

    # Collect skills to import
    skill_dirs = sorted(SOURCE_DIR.iterdir())
    if args.only:
        only_set = {s.strip() for s in args.only.split(",")}
        skill_dirs = [d for d in skill_dirs if d.name in only_set]

    imported = 0
    skipped = 0
    errors = []

    for skill_dir in skill_dirs:
        if not skill_dir.is_dir():
            continue
        slug = skill_dir.name
        if slug in SKIP_SKILLS:
            skipped += 1
            continue

        skill = parse_skill(skill_dir)
        if not skill:
            errors.append(f"{slug}: failed to parse SKILL.md")
            continue

        target = TARGET_DIR / slug
        if args.dry_run:
            print(f"  [dry-run] would import: {slug} ({skill['name']})")
            imported += 1
            continue

        target.mkdir(exist_ok=True)
        content = build_skill_md(skill)
        (target / "SKILL.md").write_text(content, encoding="utf-8")
        copy_tier3(skill, target)
        imported += 1
        print(f"  [imported] {slug}")

    print(f"\nImported: {imported}")
    print(f"Skipped (existing/meta): {skipped}")
    if errors:
        print(f"Errors: {len(errors)}")
        for e in errors:
            print(f"  ERR: {e}")


if __name__ == "__main__":
    main()
