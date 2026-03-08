# FLEET ORCHESTRATION SYSTEM — Complete Technical Manual

> How to deploy and manage parallel sub-agent workers at scale

---

## 1. ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────┐
│         MAIN SESSION (You)          │
│  - Coordinates, doesn't execute     │
│  - Monitors via subagents list      │
│  - Packages outputs when done       │
└─────────────┬───────────────────────┘
              │ spawns
    ┌─────────┼─────────┐
    ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐
│Worker1│ │Worker2│ │Worker3│
│ CSS   │ │ JS    │ │ Flask │
│ 18min │ │ 8min  │ │ 15min │
└───────┘ └───────┘ └───────┘
    │         │         │
    └─────────┴─────────┘
              │ completes
              ▼
┌─────────────────────────────────────┐
│      PACKAGE & DELIVER              │
│  - tar.gz archive                   │
│  - kimi_upload_file                 │
│  - Summary table                    │
└─────────────────────────────────────┘
```

---

## 2. SUB-AGENT SPAWN PROTOCOL

### Command Structure
```python
sessions_spawn({
    "agentId": "main",           # Always "main" for same persona
    "label": "descriptive-name", # For monitoring
    "task": "detailed prompt"    # Complete specification
})
```

### Label Naming Convention
```
project-component-attempt

Examples:
- aether-css-system
- aether-js-final
- aether-flask-rewrite-retry
- ordl-api-routes-v2
```

### Task Prompt Structure
```markdown
## GOAL
One sentence objective.

## INPUTS
- Source files: /path/to/source
- Reference docs: /path/to/docs
- Constraints: specific limitations

## OUTPUTS
List of files to create:
1. file1.py - What it does
2. file2.js - What it does

## REQUIREMENTS
- Specific requirement 1
- Specific requirement 2
- Design constraints

## SUCCESS CRITERIA
How to know it's done right.
```

---

## 3. PARALLEL DEPLOYMENT PATTERNS

### Pattern A: Independent Workstreams (Recommended)
When tasks don't depend on each other:

```python
# Spawn all at once
sessions_spawn(label="worker-css", task="Create CSS...")
sessions_spawn(label="worker-js", task="Create JS...")
sessions_spawn(label="worker-html", task="Create HTML...")
```

**Best for:** CSS, JS, templates, documentation

### Pattern B: Dependency Chain
When output of A is input to B:

```python
# Step 1: Spawn A
sessions_spawn(label="worker-design", task="Create design system...")

# Step 2: Wait for completion
subagents list  # Check status

# Step 3: Spawn B with A's output
sessions_spawn(label="worker-implement", task="Use design system to...")
```

**Best for:** Design → Implementation, API → Frontend

### Pattern C: Fan-Out with Merge
Multiple workers, one packaging step:

```python
# Spawn 3-4 workers simultaneously
# Wait for all to complete
# Package everything in one archive
```

**Best for:** Multi-file projects with distinct components

---

## 4. MONITORING COMMANDS

### Check Active Workers
```bash
subagents list
```

**Output format:**
```json
{
  "active": [
    {
      "label": "worker-name",
      "status": "running",
      "runtime": "5m",
      "model": "kimi-coding/k2p5"
    }
  ],
  "recent": [
    {
      "label": "completed-worker",
      "status": "done",
      "totalTokens": 45000
    }
  ]
}
```

### Poll for Completion
```bash
subagents list  # Run every 1-2 minutes
```

Don't spam. Workers take 5-20 minutes depending on task size.

---

## 5. TASK DECOMPOSITION STRATEGY

### How to Split Work

| Original Task | Decomposition | Workers |
|--------------|---------------|---------|
| "Build a website" | CSS system, JS effects, HTML templates, Backend | 4 |
| "Create API" | Routes, Models, Tests, Documentation | 4 |
| "Refactor codebase" | Analysis, Core changes, Tests, Migration guide | 4 |
| "Design system" | Colors, Typography, Components, Documentation | 4 |

### Worker Scope Guidelines

**Too Big (Will timeout/fail):**
- "Build entire application"
- "Create all files"
- "Do everything"

**Just Right:**
- "Create CSS design system with variables, components, utilities"
- "Build Flask routes for dashboard, image, text pages"
- "Generate JavaScript effects: binary rain, typewriter, hex clock"

**Too Small (Overhead not worth it):**
- "Create one function"
- "Write 5 lines of CSS"

### Optimal Worker Count
- **2-3 workers:** Simple projects
- **4-5 workers:** Medium complexity
- **6+ workers:** Complex projects with clear boundaries

---

## 6. RATE LIMIT HANDLING

### When Workers Fail
```
⚠️ API rate limit reached. Please try again later.
```

### Recovery Protocol
1. **Wait 2-3 minutes** — Don't immediately respawn
2. **Check which workers survived** — Some may still be running
3. **Respawn one at a time** — With 30-60s delays between
4. **Reduce task size if repeated failures** — Split smaller

### Prevention
- Stagger spawns by 30s when launching 4+ workers
- Don't respawn failed workers immediately
- Monitor with `subagents list` before respawning

---

## 7. COMPLETION & PACKAGING PROTOCOL

### Step 1: Verify All Workers Done
```bash
subagents list
# Should show: 0 active, all in "recent"
```

### Step 2: Create Archive
```bash
cd /workspace
tar -czf project-complete.tar.gz \
  file1.py \
  file2.js \
  templates/ \
  static/ \
  README.md
```

### Step 3: Upload
```python
kimi_upload_file({
    "paths": ["/workspace/project-complete.tar.gz"]
})
```

### Step 4: Deliver Summary
```markdown
## ✅ PROJECT COMPLETE

### Files Created:
| File | Size | Description |
|------|------|-------------|
| app.py | 12KB | Flask application |
| style.css | 45KB | Design system |

### How to Use:
1. Extract: `tar -xzf project-complete.tar.gz`
2. Install: `pip install -r requirements.txt`
3. Run: `python app.py`
```

---

## 8. COMMUNICATION PATTERNS

### Main Agent → Sub-Agent
**Clear specification** in task prompt:
- Exact file paths
- Specific requirements
- Success criteria
- Output format

### Sub-Agent → Main Agent
**Structured completion report:**
```markdown
## Summary
What was accomplished

## Files Created
| File | Size | Lines |

## Key Features
- Feature 1
- Feature 2

## Usage Example
\`\`\`html
<!-- Example -->
\`\`\`

Stats: runtime XmXs • tokens Xk
```

### System Messages
When sub-agent completes, main agent receives:
```
[System Message] A subagent task "label" just completed successfully.
Result: [completion report]
```

**Main agent must:**
1. Convert system message to user-friendly summary
2. Not copy system message verbatim
3. Send update or reply "NO_REPLY" if already covered

---

## 9. ERROR HANDLING

### Worker Failure Types

| Error | Cause | Fix |
|-------|-------|-----|
| Rate limit | Too many requests | Wait 2-3 min, retry |
| Timeout | Task too big | Split into smaller workers |
| Parse error | Malformed output | Add explicit format instructions |
| Missing files | Wrong paths | Verify paths in task prompt |

### When All Workers Fail
1. Reduce scope — split into smaller chunks
2. Simplify prompts — remove ambiguity
3. Spawn sequentially — not parallel
4. Debug with single worker first

---

## 10. ADVANCED PATTERNS

### Pattern: Cascading Refinement
```
Worker 1: Generate v1
Worker 2: Review and improve
Worker 3: Final polish
```

### Pattern: A/B Testing
```
Worker A: Implementation approach A
Worker B: Implementation approach B
Compare outputs, pick best
```

### Pattern: Specialized Tutors
```
Worker 1: Security review
Worker 2: Performance optimization
Worker 3: Accessibility check
Worker 4: Documentation
```

### Pattern: Recursive Decomposition
```
Main: "Build website"
  └─ Worker 1: "Design system"
       └─ Worker 1a: "Color palette"
       └─ Worker 1b: "Typography"
       └─ Worker 1c: "Components"
  └─ Worker 2: "Backend"
  └─ Worker 3: "Frontend"
```

---

## 11. QUALITY ASSURANCE

### Before Spawning
- [ ] Task is specific and bounded
- [ ] File paths are correct
- [ ] Requirements are clear
- [ ] Output format is specified

### During Execution
- [ ] Monitor with `subagents list` every 1-2 min
- [ ] Don't interrupt running workers
- [ ] Wait for completion before respawning

### After Completion
- [ ] Verify all expected files exist
- [ ] Check file sizes (0 bytes = failure)
- [ ] Test critical functionality
- [ ] Package and upload

---

## 12. EXAMPLE: COMPLETE WORKFLOW

### Task: Build ORDL Dashboard

**Step 1: Decompose**
```
Worker 1: CSS design system (monochrome)
Worker 2: JavaScript effects (binary rain, typewriter)
Worker 3: Flask backend (routes, templates)
Worker 4: HTML templates (dashboard, settings)
```

**Step 2: Spawn**
```python
sessions_spawn(label="ordl-css", task="Create CSS...")
# Wait 30s
sessions_spawn(label="ordl-js", task="Create JS...")
# Wait 30s
sessions_spawn(label="ordl-flask", task="Create Flask...")
# Wait 30s
sessions_spawn(label="ordl-templates", task="Create HTML...")
```

**Step 3: Monitor**
```bash
# Run every 2 minutes
subagents list
```

**Step 4: Complete**
```bash
# When all done
tar -czf ordl-dashboard.tar.gz *.py *.css *.js templates/
kimi_upload_file({"paths": ["ordl-dashboard.tar.gz"]})
```

**Step 5: Summarize**
```markdown
## ✅ ORDL Dashboard Complete

| Component | File | Size |
|-----------|------|------|
| CSS | ordl-zero.css | 69KB |
| JS | binary-effects.js | 14KB |
| Backend | app.py | 12KB |
| Templates | templates/ | 28KB |

### Deploy:
1. `pip install flask`
2. `python app.py`
3. Open http://localhost:5000
```

---

## 13. ANTI-PATTERNS (DON'T DO)

❌ **Spawn 10+ workers at once** — Rate limit guaranteed
❌ **Respawn immediately on failure** — Exacerbates rate limits  
❌ **Vague task descriptions** — Workers produce garbage
❌ **Not monitoring** — Surprised by failures
❌ **Tasks with dependencies** — Spawned as independent
❌ **No success criteria** — Don't know when done
❌ **Giant single worker** — Will timeout or fail

---

## 14. TOOL REFERENCE

### sessions_spawn
```python
{
    "agentId": "main",                    # Always "main"
    "label": "unique-descriptive-name",   # For monitoring
    "task": "Complete task description"   # Full specification
}
```

### subagents
```python
# List all workers
subagents({"action": "list"})

# Check specific worker
subagents({"action": "list", "target": "worker-label"})

# Kill stuck worker
subagents({"action": "kill", "target": "worker-label"})

# Send message to worker
subagents({"action": "steer", "target": "worker-label", "message": "..."})
```

### kimi_upload_file
```python
{
    "paths": [
        "/absolute/path/to/file1",
        "/absolute/path/to/file2"
    ]
}
# Max 5 files per call
```

---

## 15. PERFORMANCE METRICS

### Typical Worker Runtimes
| Task Type | Duration | Tokens |
|-----------|----------|--------|
| CSS system | 15-20 min | 50-100k |
| JS effects | 5-10 min | 20-40k |
| HTML template | 5-8 min | 15-30k |
| Flask routes | 10-15 min | 30-60k |
| Documentation | 3-5 min | 10-20k |

### Parallel Limits
- **Safe:** 3-4 workers simultaneously
- **Maximum:** 5 workers (risk rate limits)
- **Rate limit cooldown:** 2-3 minutes

---

*This is the complete fleet orchestration system. Use it to deploy at scale.*
