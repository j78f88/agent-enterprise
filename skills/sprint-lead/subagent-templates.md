# Sprint Lead — Subagent Prompt Templates

## Implementation Subagent Prompt Template

Construct this prompt for each task and pass it to a subagent:

```
Context:
- Sprint: {N}
- Task: {task_number} — {task_title}
- Description: {task_description from PLAN.md}
- Acceptance criteria: {criteria from PLAN.md}
- Files to touch (create or modify): {file_paths from PLAN.md task Files: annotation}
  Note: Some files may not exist yet — create them. Consult the plan's "Files to Create/Modify" section to distinguish new vs existing.
- Files to reference: {related files for context}

Rules:
- Follow {{paths.copilot_instructions}} for all code patterns
- Commit format: `{type}: Sprint {N} — {description}` (types: feat|fix|test|refactor)
- Run `{{commands.typecheck}}` and `{{commands.lint}}` after edits — fix before committing
- Run scoped tests for touched files only (e.g., the component's test file, or `{{commands.test}}` if a store was modified). Do NOT run the full test suite — @qa handles that in Phase 3.
- If a new component is created, add a basic test file

Return EXACTLY this JSON:
{
  "status": "done" | "blocked" | "partial",
  "commits": ["abc1234 feat: Sprint N — description"],
  "filesCreated": ["path/to/new.ts"],
  "filesModified": ["path/to/changed.ts"],
  "testsAdded": 3,
  "testsTotal": 150,
  "linesAdded": 120,
  "linesRemoved": 30,
  "fixIterations": 0,
  "complexityAssessment": "moderate",
  "surprises": null | "description of anything unexpected",
  "blockerReason": null | "description of what blocked",
  "notes": "anything sprint-lead should know"
}

After all commits for this task, run `git diff --stat HEAD~N` where N is the number of commits in your `commits` array. Report totals in `linesAdded`/`linesRemoved`. Assess complexity per `{{paths.instructions_dir}}/retro-report.instructions.md` § Complexity Scale.
```

---

## Fix Subagent Prompt Template

Used by Phase 2.5 (safety-net failures), Phase 3 (gate CRITICAL findings), and Phase 4 (review CRITICAL findings). Keep fixes narrow — fix subagents must not drift into refactoring.

```
Context:
- Sprint: {N}
- Issue: {one-line description from the failing check or review finding}
- Files: {affected file paths}
- Error output: {stderr, test failure, or finding text}

Rules:
- Scope: fix ONLY this issue. No refactoring, no scope creep.
- Commit format: `fix: Sprint {N} — {description}`
- Re-run the same check that caught the issue (typecheck / lint / specific test) to verify the fix.
- Do NOT run the full test suite.

Return EXACTLY this JSON:
{
  "status": "done" | "blocked",
  "commits": ["abc1234 fix: Sprint N — description"],
  "filesModified": ["path/to/changed.ts"],
  "linesChanged": 15,
  "rootCause": "brief description of the root cause",
  "notes": "what was fixed and how"
}
```
