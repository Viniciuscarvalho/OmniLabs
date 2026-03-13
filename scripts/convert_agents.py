#!/usr/bin/env python3
"""Convert markdown agent definitions to OmniLabs YAML format.

Parses .md files with YAML frontmatter (--- delimited) and markdown body,
outputs OmniLabs-compatible .yaml files.

Usage:
    python scripts/convert_agents.py <source_dir> [target_dir]

    source_dir: Directory containing .md agent files
    target_dir: Output directory (default: ~/.omnilabs/agents/)
"""

import re
import sys
from pathlib import Path

# Agent metadata not present in the source .md files
AGENT_META = {
    "seo-strategist": {
        "icon": "\U0001f50d",
        "focus": "Organic search growth — keyword research, technical SEO audits, on-page optimization",
        "tags": ["marketing", "seo", "growth"],
    },
    "content-strategist": {
        "icon": "\U0001f4dd",
        "focus": "Content strategy — editorial calendars, content audits, distribution planning",
        "tags": ["marketing", "content", "strategy"],
    },
    "copywriter": {
        "icon": "\u270d\ufe0f",
        "focus": "Conversion-oriented copy — landing pages, ads, emails, product descriptions",
        "tags": ["marketing", "content", "conversion"],
    },
    "social-media-manager": {
        "icon": "\U0001f4f1",
        "focus": "Social media strategy — content calendars, engagement, platform optimization",
        "tags": ["marketing", "social", "engagement"],
    },
    "community-manager": {
        "icon": "\U0001f91d",
        "focus": "Community building — engagement programs, advocacy, feedback loops",
        "tags": ["marketing", "community", "engagement"],
    },
    "product-marketing-manager": {
        "icon": "\U0001f3af",
        "focus": "Product positioning — messaging frameworks, launch plans, competitive intel",
        "tags": ["marketing", "product", "strategy"],
    },
    "gtm-strategist": {
        "icon": "\U0001f680",
        "focus": "Go-to-market strategy — launch planning, channel strategy, market entry",
        "tags": ["marketing", "gtm", "strategy"],
    },
    "email-marketing-specialist": {
        "icon": "\U0001f4e7",
        "focus": "Email marketing — automation flows, segmentation, deliverability, A/B testing",
        "tags": ["marketing", "email", "automation"],
    },
    "lifecycle-marketing-manager": {
        "icon": "\U0001f504",
        "focus": "Customer lifecycle — onboarding, retention, reactivation, churn prevention",
        "tags": ["marketing", "lifecycle", "retention"],
    },
    "marketing-analyst": {
        "icon": "\U0001f4ca",
        "focus": "Marketing analytics — attribution, funnel analysis, ROI measurement",
        "tags": ["marketing", "analytics", "data"],
    },
    "cro-specialist": {
        "icon": "\U0001f4c8",
        "focus": "Conversion rate optimization — A/B testing, funnel optimization, UX analysis",
        "tags": ["marketing", "conversion", "optimization"],
    },
    "pr-strategist": {
        "icon": "\U0001f4e2",
        "focus": "Public relations — media outreach, press releases, crisis communication",
        "tags": ["marketing", "pr", "communications"],
    },
    "communications-manager": {
        "icon": "\U0001f4ac",
        "focus": "Corporate communications — internal comms, brand voice, stakeholder messaging",
        "tags": ["marketing", "communications", "brand"],
    },
}


def parse_md_agent(path: Path) -> dict | None:
    """Parse a markdown agent file with YAML frontmatter."""
    text = path.read_text(encoding="utf-8")

    # Split frontmatter from body
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', text, re.DOTALL)
    if not match:
        print(f"  Skipping {path.name}: no YAML frontmatter", file=sys.stderr)
        return None

    frontmatter = match.group(1)
    body = match.group(2).strip()

    # Extract name from frontmatter
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if not name_match:
        print(f"  Skipping {path.name}: no name in frontmatter", file=sys.stderr)
        return None

    agent_id = name_match.group(1).strip()
    return {"id": agent_id, "system_prompt": body}


def to_yaml(agent_id: str, system_prompt: str) -> str:
    """Convert agent data to OmniLabs YAML format."""
    meta = AGENT_META.get(agent_id, {
        "icon": "\U0001f916",
        "focus": f"Specialist agent: {agent_id}",
        "tags": ["marketing"],
    })

    # Human-readable name from id
    name = agent_id.replace("-", " ").title()

    # Build key_outputs from first few ## headings in the prompt
    headings = re.findall(r'^## (.+)$', system_prompt, re.MULTILINE)
    key_outputs = headings[:4] if headings else [f"{name} analysis report"]

    # Format tags as inline YAML list
    tags_str = "[" + ", ".join(meta["tags"]) + "]"

    # Format key_outputs as block list
    ko_lines = "\n".join(f"  - {ko}" for ko in key_outputs)

    # Indent system_prompt by 2 spaces for | block scalar
    indented_prompt = "\n".join(f"  {line}" if line.strip() else "" for line in system_prompt.split("\n"))

    return f"""id: {agent_id}
name: {name}
icon: "{meta['icon']}"
focus: {meta['focus']}
tags: {tags_str}
key_outputs:
{ko_lines}
system_prompt: |
{indented_prompt}
"""


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <source_dir> [target_dir]", file=sys.stderr)
        sys.exit(1)

    source_dir = Path(sys.argv[1]).expanduser()
    target_dir = Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else Path.home() / ".omnilabs" / "agents"

    if not source_dir.is_dir():
        print(f"Error: {source_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    target_dir.mkdir(parents=True, exist_ok=True)

    skip_files = {"README.md", "install.sh"}
    converted = 0

    for path in sorted(source_dir.glob("*.md")):
        if path.name in skip_files:
            continue

        agent = parse_md_agent(path)
        if agent is None:
            continue

        yaml_content = to_yaml(agent["id"], agent["system_prompt"])
        out_path = target_dir / f"{agent['id']}.yaml"
        out_path.write_text(yaml_content, encoding="utf-8")
        print(f"  Converted: {path.name} → {out_path.name}")
        converted += 1

    print(f"\nConverted {converted} agents to {target_dir}")


if __name__ == "__main__":
    main()
