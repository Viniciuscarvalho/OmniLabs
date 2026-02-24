---
name: continuous-learning
description: |
  Captures and retrieves knowledge from OmniLabs strategic analysis sessions.
  Manages two types of memories: learnings (discoveries, patterns, workarounds)
  and decisions (architecture choices, conventions, analysis methodology).
  Active during every analysis session, coding task, and evaluation run.
  Automatically evaluates whether current work contains valuable knowledge
  and saves memories as files in <project>/.claude/memories/.
allowed-tools:
  - Write
  - Read
  - Glob
  - Edit
  - Bash
  - mcp__docs-mcp-server__search_docs
  - mcp__docs-mcp-server__list_libraries
  - AskUserQuestion
  - TaskCreate
  - TaskUpdate
  - TaskList
---

# Continuous Learning Skill

Extract reusable knowledge from OmniLabs analysis sessions and save it as memory files in `<project>/.claude/memories/`.

## Memory Types

### Learnings (`learning_<topic>_<specific>`)

Knowledge discovered through analysis, debugging, or investigation that wasn't obvious beforehand.

**Extract when:**
- Solution required significant investigation (not a documentation lookup)
- Discovered a non-obvious pattern in codebase analysis
- Found a workaround for an agent, tool, or framework limitation
- Error message was misleading — root cause was unexpected
- Evaluation revealed surprising agent behavior

**Examples:** `learning_analysis_tam-estimation-saas`, `learning_evaluation_false-positive-moat`, `learning_tooling_ollama-embedding-limits`, `learning_debugging_grader-exit-codes`

### Decisions (`decision_<domain>_<topic>`)

Deliberate choices about how OmniLabs or the analyzed project should work.

**Extract when:**
- Architecture or methodology choice made with reasoning
- Convention or standard established
- Scoring calibration adjusted based on evidence
- Tool or library selected over alternatives
- User says "let's use X", "I prefer Y", "from now on..."
- Trade-off resolved between competing concerns

**Domain prefixes:**

| Domain | Description | Examples |
|--------|-------------|---------|
| `analysis` | Strategic analysis patterns and methodologies | `decision_analysis_scoring-methodology` |
| `evaluation` | Eval framework choices, thresholds, grader logic | `decision_evaluation_pass-threshold` |
| `agent` | Agent behavior, prompt engineering, output format | `decision_agent_score-range-calibration` |
| `framework` | OmniLabs architecture, extension patterns | `decision_framework_hook-registration` |
| `tooling` | Tool usage, MCP servers, CLI configurations | `decision_tooling_embedding-model-choice` |
| `debugging` | Debugging approaches, error resolution strategies | `decision_debugging_grader-test-strategy` |

---

## Extraction Workflow

### Step 1: Evaluate the Current Task

After completing any task, ask:
- Did this require non-obvious investigation or debugging?
- Was a choice made about architecture, methodology, or approach?
- Did the user express a preference or convention?
- Would future analysis sessions benefit from having this documented?
- Did an eval reveal something about agent behavior?

If NO to all → skip. If YES to any → continue.

### Step 2: Search Existing Knowledge

**Always search docs-mcp-server first** (semantic search across memories):

```
mcp__docs-mcp-server__search_docs(library: "omnilabs-memories", query: "<topic>")
```

**Fall back to file listing** if search_docs returns no results:

```
Glob(pattern: ".claude/memories/*.md")
```

Determine if: update an existing memory, cross-reference related memories, or knowledge is already captured.

### Step 3: Research (When Appropriate)

**For general topics** — use web search:
```
WebSearch(query: "<topic> best practices 2026")
```

**Skip research for:** project-specific conventions, personal preferences, time-sensitive captures.

### Step 4: Structure and Save

Read [references/templates.md](references/templates.md) for the full template structures.

**Choose the right template:**
- Debugging discovery or workaround → **Learning Template**
- Architecture or methodology choice → **Decision Template**
- Recurring analysis approach → **Analysis Pattern Template**
- Evaluation insight about agent behavior → **Eval Finding Template**

**Save:**
```
Write(file_path: "<project>/.claude/memories/<category>_<topic>_<specific>.md", content: "<structured markdown>")
```

**Update existing:**
```
Edit(file_path: "<project>/.claude/memories/<existing_name>.md", old_string: "<section to update>", new_string: "<updated section>")
```

### Step 5: Verify

- Confirm the file was created/updated successfully
- Verify naming follows the convention
- Check that the content matches the template structure

---

## Quality Gates

Before saving any memory, verify:

- [ ] Name follows the correct pattern (`learning_` or `decision_<domain>_`)
- [ ] Content uses the appropriate template from references/templates.md
- [ ] Knowledge is verified to work (not theoretical)
- [ ] Content is specific enough to be actionable
- [ ] Content is general enough to be reusable across projects
- [ ] No sensitive information (credentials, internal URLs, API keys)
- [ ] Does not duplicate existing memories (verified via search)
- [ ] References included if external sources were consulted

---

## Retrospective Mode

When `/retrospective` is invoked:

1. Review conversation history for extractable knowledge
2. Search existing memories via `mcp__docs-mcp-server__search_docs` (fall back to `Glob(".claude/memories/*.md")`)
3. List candidates with brief justifications
4. Extract top 1-3 highest-value memories
5. Report what was created and why

---

## Retrieval Protocol

**Before starting any analysis task**, search the knowledge base:

1. Use `mcp__docs-mcp-server__search_docs` with library `omnilabs-memories` and keywords from the task
2. Try 2-3 keyword variations for broader coverage
3. Review the top 3-5 results for applicable patterns, decisions, or findings
4. Note any outdated or conflicting memories for review
5. Proceed with analysis enriched by prior knowledge

---

## Tool Reference

| Tool | Purpose |
|------|---------|
| `mcp__docs-mcp-server__search_docs` | **Primary:** Semantic search across memories |
| `mcp__docs-mcp-server__list_libraries` | List indexed libraries |
| `Glob` | **Fallback:** List all memory files (`.claude/memories/*.md`) |
| `Read` | Read a specific memory file |
| `Write` | Create new memory file |
| `Edit` | Update existing memory file |
| `Bash` | Remove outdated memory file (`rm`) |
| `WebSearch` | Research general topics before saving |
