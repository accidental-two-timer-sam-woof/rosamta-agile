# 04 Working prototype

- Date: 2026-11-10
- Who: Stanley (with AI); review by Jonas and SamWang
- Tool and model: Claude (Opus 5.5), in the project chat
- Purpose: build a working prototype of the Must stories (and most Should stories) for the demo, with one test per acceptance criterion

## Prompt

Build the basic working rosamta from our accepted stories, in Python with no extra dependencies. Cover every Must story, add the quick Should stories, and write a test for each acceptance criterion. Commit it story by story.

## AI output

The code in `src/rosamta`, the tests in `tests/` and the CI workflow, as committed in this PR.

## Decisions the AI made while coding (PO to confirm)

| Decision | Why it matters | PO decision |
| --- | --- | --- |
| A failed preflight exits with code 1 | S20 did not define this (the open question from the activity diagram) | Accepted by Stanley (2026-11-11). S20 (#26) and the activity diagram updated |
| Module, manifest and profile files are TOML | No story fixed a format; TOML needs no extra library | (fill in) |
| The Host ID defaults to the hostname the first time, then stays fixed in local settings | Follows the S07 change request | Accepted by Stanley (2026-11-11). S18 (#24) updated to say Host ID |
| An old output kept because of hand edits also gives exit code 2 | S15 and S20 did not say | (fill in) |
| Python instead of Rust | Fastest to build for the demo; the AI-agent team uses Rust | (fill in) |

## Not done

- S10 checks missing programs but not missing fonts (font detection differs on every OS)
- Windows paths are supported in the manifest but not tested

## Where the AI was wrong

- The first version of preview hid the diff for a hand-edited file. S14 says preview must show it. A test caught it and it was fixed before commit.
- (team: add anything found in review)

## Time saved or lost

(fill in)
