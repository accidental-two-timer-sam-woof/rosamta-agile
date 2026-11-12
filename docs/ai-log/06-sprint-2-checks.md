# 06 Sprint 2 checks against the acceptance criteria

The Sprint 2 work is checking each story against its criteria (see `sprints/sprint-2-plan.md`). Each member adds a section for their own AI use. #46 and #48 both said they would be recorded in 06, so this file collects them.

Still to add, by the PR author:

| PR | Author |
| --- | --- |
| #38 Save the Host ID on the first apply | SamWang |
| #41 Cover the S10 and S18 criteria | Stanley |
| #43 Unwritable settings folder | SamWang |
| #44 Record the PO decisions from the #41 review | Stanley |
| #47 Target paths in the S16 query test | SamWang |
| #48 Exit 3 and a JSON error for wrong arguments | Stanley |

## Jonas: S21 error file (#46)

- Date: 2026-11-12
- Who: Jonas
- Tool and model: Claude Code (Claude Opus 5.5)
- Purpose: meet the second S21 criterion, which asks the JSON error to name the file involved

### Prompt

Summarized; the conversation was in Chinese. Check S21 against the code and make every `--json` error name the file involved.

### AI output

The change in #46: every rosamta error carries the file involved, and the JSON error has `code`, `file` and `message`. A test for each kind of error.

### Accepted and rejected

| Item | Decision | Reason | Approved by |
| --- | --- | --- | --- |
| `file` is `null` when no file is involved (an unknown name in `rosamta query`) | Accepted | Always having the key is easier for scripts | Jonas |
| A missing key in a built-in template names the module, not the template | Accepted, chosen by Jonas | A built-in template cannot be edited, so the module is the file to fix | Jonas |
| A failed preflight names the first output; the full list stays in `problems` | Accepted | | Jonas |

### Where the AI was wrong

Nothing found in review. The usage errors from argparse were left out and opened as #45.

## Jonas: Sprint 2 health check and story checks

- Date: 2026-11-12
- Who: Jonas
- Tool and model: Claude Code (Claude Opus 5.5)
- Purpose: check how the team follows Scrum, check S14, S15 and S21 against their criteria, review #48, and draft this day's daily record

### Prompt

Summarized; the conversation was in Chinese.

1. Are we following Scrum? Summarize the epics, sprints, stories, UML and important PRs. What is left for each of us? How do we compare with the other two teams?
2. Check everything again (Jonas pointed out wrong claims about #44 and #47), then make a web page of the result.
3. Split the problems by role, and do the ones that are mine.

### AI output

- A health check page: what follows Scrum, what to fix, a story table, the to-do list for each role, and a comparison with the other two teams
- S14 (#20) and S15 (#21): stronger tests. Before, an `--overwrite` that wrote an empty file passed, and an edited old output that exited 0 passed. Each new test was checked by breaking the code and seeing it fail
- S21 (#27): `rosamta apply --json`, as written in the criterion, failed with a usage error. A fix that builds on #48
- A review of #48 and a draft of this day's daily record

### Accepted and rejected

| Item | Decision | Reason | Approved by |
| --- | --- | --- | --- |
| First answer: #44 and #46 approved with no notes; S03, S10 and S18 skipped In review | Rejected | Wrong. Jonas noticed, and a second check of the review comments and the board history showed both claims were false | Jonas |
| S22 (#28) was closed by #47, an S16 PR, without a PO review | Accepted | The board history shows it moved straight from In progress to Done when #47 merged | Jonas |
| Switch the prototype from Python to Rust | Rejected for now | `docs/ai-log/04-prototype.md` records the PO's choice of Python. Changing it is a PO decision and would not fit before the midterm | Jonas |
| The S14, S15 and S21 changes | Accepted after review | Jonas reads each diff before it is pushed | Jonas |
| Daily record: Done column and notes | Accepted | Other members write their own Next and Blockers | Jonas |

### Where the AI was wrong

- The first answer read only the review body of each PR, not the separate comments, so it said #44 and #46 had no review notes. Jonas had written the checks in a separate comment on #44, and Stanley in an inline comment on #46.
- It used a stale local `main` for the commit counts.
- It said S03, S10 and S18 skipped In review. The board history shows the PO moved them through In review.

### Time saved or lost

(Jonas to fill in)

## SamWang: S22 actionable errors (#52)

- Date: 2026-11-12
- Who: SamWang
- Tool and model: Claude Code (Claude Opus 5.5); review by Codex CLI and CodeRabbit
- Purpose: check S22 (#28) against the code: every error should say what failed, where, and what to change

### Prompt

Summarized; the conversation was in Chinese.

1. Go through the error paths of every command and fix the errors that crash with a traceback or give no hint. Hold back the `get` and `render` messages until #48 merges, because #48 changes the same part of `cli.py`.
2. Run a Codex review and fix what it finds until it finds nothing, then open the PR and fix what CodeRabbit finds. CI must pass.
3. Fix the points in Jonas's review.

### AI output

- An audit script that triggered each error path: unreadable, non-UTF-8 and FIFO config files, a damaged `state.json`, unreadable outputs, and unsearchable folders. It listed the paths that crashed with a traceback or had no hint.
- The fixes in #52:
  - one shared reader in `paths.py`
  - a preflight check for the state record
  - hints for the config, `query`, `get` and `render` errors
  - a test for each case, each checked to fail on `main`

### Accepted and rejected

| Item | Decision | Reason | Approved by |
| --- | --- | --- | --- |
| One shared reader that opens without blocking and rejects anything that is not a regular file | Accepted | FIFO, permission and encoding errors are handled in one place, and a FIFO can no longer hang rosamta (S19) | SamWang |
| Preflight checks that the state record can be written | Accepted after a change | The first version also required a writable state folder when `state.json` already existed. Codex found that this stopped `apply` for a read-only folder with a writable `state.json`. Now only a new `state.json` needs a writable folder | SamWang |
| An old output that rosamta cannot read is kept and reported, not removed | Accepted | rosamta cannot tell whether it was edited, so it treats it like an edited file | SamWang |
| `get` and `render` hints in a separate commit after #48 | Accepted | Avoided a conflict with #48 | SamWang |
| Jonas's review: the modules folder case, and `Refs #28` instead of `Closes #28` | Accepted | Both were right. The same check found that `init` had the problem too, so it was fixed in the same commit | SamWang |

### Where the AI was wrong

- The audit missed the modules folder: `Path.glob` skips a folder it cannot list without raising, so a locked folder looked empty. Jonas found it in review. Fixing it showed the same problem in `init`'s `is_file()` check.
- The first state record check blocked `apply` in a case that worked before. Codex found it.
- The audit script built one template path wrong (`templates/bash` instead of `templates/bash.tmpl`), so that case first looked fine.
- Twice, a check that a new test fails on `main` ran against the fixed code by mistake, so it proved nothing. Both checks were redone.
- The PR used `Closes #28` from the template. The Sprint 2 plan says story PRs use `Refs #n`, so that the PO closes the story after the review. Jonas pointed this out.

### Time saved or lost

(SamWang to fill in)
