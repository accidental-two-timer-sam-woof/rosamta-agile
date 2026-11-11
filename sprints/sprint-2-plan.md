# Sprint 2 plan

- Dates: 2026-11-11 to 2026-11-12 (Iteration 2)
- Goal: accept the 8 Should stories, each checked against its acceptance criteria, and get the midterm hand-in ready
- Team: Stanley (Product Owner), Jonas (Scrum Master), SamWang (design lead)
- Committed: 8 stories, 21 points (AI suggested 21). Sprint 1 velocity was 33 points.

## Planning poker

Held on Discord on 2026-11-12, just after midnight. Each member posted their votes. The AI's suggested points are written in each issue, so the votes were not blind to them.

Rule (from the Sprint 1 retro): when votes are more than one step apart, the highest and lowest voters explain their reasons and we vote again before taking the median.

| Story | AI | Jonas | SamWang | Stanley | Final | Note |
| --- | --- | --- | --- | --- | --- | --- |
| S03 Override a built-in template (#8) | 3 | 2 | 2 | 2 | 2 | Everyone agreed, lower than the AI |
| S10 Preflight checks (#15) | 3 | 3 | 3 | 3 | 3 | Everyone agreed. Voted before the PO moved the font check to S24 (#39) |
| S14 Overwrite a drifted file (#20) | 2 | 2 | 2 | 2 | 2 | Everyone agreed |
| S15 Clean up old outputs (#21) | 3 | 3 | 3 | 3 | 3 | Everyone agreed |
| S16 Query outputs of a module (#22) | 2 | 2 | 2 | 2 | 2 | Everyone agreed |
| S18 Initialize a new machine (#24) | 3 | 3 | 3 | 3 | 3 | Everyone agreed |
| S21 Machine-readable output (#27) | 3 | 3 | 3 | 3 | 3 | Everyone agreed |
| S22 Actionable error messages (#28) | 2 | 5 | 3 | 2 | 3 | Two steps apart, so the retro rule applied. See below |

### S22 discussion

Jonas and Stanley wrote in Chinese; their reasons are translated.

- **Jonas (5):** the second criterion says "given any command", so the range felt large.
- **Stanley (2):** read the acceptance criteria literally. The missing-key error already names the template, the line, the key and the module file to fix, and errors already go to standard error and results to standard output. So the work is mainly wording and tests.
- **SamWang (3):** more than 2, because the story says every error must say what failed, where and what to change, so each command's error paths (manifest, profiles, preflight, rollback, JSON errors) must be checked and tested. Less than 5, because errors already share one type and one reporting place, and there is no new mechanism or the risk of S12 or S13. Similar in size to S06 (3).
- **Re-vote:** after hearing the reasons, all three kept their votes, so we took the median: **3**.

### What we learned

- The team agreed on 7 of 8 stories in the first round. In Sprint 1 it was 3 of 12. We will ask why in the Sprint 2 retro.
- The team's total (21) equals the AI's, but S03 went down and S22 went up.
- The re-vote rule from the Sprint 1 retro was used for the first time.

## Sprint backlog

| Story | Points | Owner |
| --- | --- | --- |
| S03, S10, S18 | 8 | Stanley |
| S14, S15, S21 | 8 | Jonas |
| S16, S22 | 5 | SamWang |

SamWang has fewer points because he is also fixing CI. Owners can be changed on the board.

The code for these stories is already in the prototype (#33). For each story, the owner:

1. Checks every acceptance criterion against the code and its test
2. Adds a missing test or fix in its own PR, with `Refs #n`
3. Moves the card to In review. The PO accepts or rejects it in the Sprint 2 review

## Also in this sprint

- Midterm hand-in: report, slides, 分工表, one-page AI usage log, repo link, zip
- CI: the Linux runner cannot reach the Ubuntu package servers (SamWang)

## Definition of done

Same as Sprint 1, plus (from the Sprint 1 retro): every approval says what the reviewer checked.
