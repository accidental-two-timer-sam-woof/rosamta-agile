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
