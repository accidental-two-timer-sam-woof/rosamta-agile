# Sprint 1 plan

- Dates: 2026-11-10 (1 day)
- Goal: turn the 12 Must stories into accepted, estimated requirements, and draft the use case diagram
- Team: Stanley (Product Owner), Jonas (Scrum Master), SamWang (design lead)
- Committed: 12 stories, 33 points (AI suggested 35)

## Planning poker

Held on Discord on 2026-11-10. Jonas and SamWang voted blind, without seeing the AI's points. Stanley had already seen the AI's points while reviewing the draft as PO, so his votes matched the AI's and are not counted as blind.

Rule: when the votes are within one step of each other, we take the median. When they are further apart, the highest and lowest voters explain their reasons and we vote again.

| Story | AI | Jonas | SamWang | Stanley | Final | Note |
| --- | --- | --- | --- | --- | --- | --- |
| S01 Shared values in a module (#6) | 3 | 1 | 2 | 3 | 2 | Reading one file and substituting values is simple |
| S02 Built-in templates (#7) | 3 | 2 | 3 | 3 | 3 | |
| S05 Target paths per OS (#10) | 3 | 2 | 2 | 3 | 2 | Just a path per OS in the manifest |
| S06 Manifest validation (#11) | 2 | 3 | 3 | 2 | 3 | Two different checks (outside home, duplicate paths), higher than the AI |
| S07 Profiles by OS and hostname (#12) | 3 | 3 | 3 | 3 | 3 | Everyone agreed |
| S09 Preview changes (#14) | 3 | 3 | 3 | 3 | 3 | Everyone agreed |
| S11 Apply outputs (#16) | 3 | 2 | 3 | 3 | 3 | |
| S12 Roll back a failed apply (#17) | 5 | 5 | 5 | 5 | 5 | Everyone agreed |
| S13 Detect hand edits (#19) | 3 | 8 | 5 | 3 | 5 | Widest spread, so we discussed it and voted again. Drift needs a record of what rosamta last wrote, which the AI's estimate ignored |
| S19 Never wait for input (#25) | 2 | 1 | 1 | 2 | 1 | Smaller than the AI thought |
| S20 Documented exit codes (#26) | 2 | 1 | 1 | 2 | 1 | Smaller than the AI thought |
| S23 Back up existing files (#18) | 3 | 2 | 2 | 3 | 2 | |

### What we learned

- The team rated simple, rule-like stories (S19, S20, S05, S01) lower than the AI did.
- The team rated S06 and S13 higher. Both have hidden work the AI's estimate missed: two separate checks for S06, and storing what was last written for S13.
- The AI gave almost every story 2 or 3. Its estimates were safe but did not separate easy stories from hard ones.

## Sprint backlog

| Story | Points | Owner |
| --- | --- | --- |
| S01, S02, S05, S06 | 10 | Stanley |
| S07, S09, S11, S12 | 14 | Jonas |
| S13, S19, S20, S23 | 9 | SamWang |

Owners can be changed on the board. The use case diagram (SamWang) covers all 12 stories.

## Definition of done

- Every acceptance criterion is testable and the PO has accepted the story
- Story points are agreed by the team
- The story appears in the use case diagram
