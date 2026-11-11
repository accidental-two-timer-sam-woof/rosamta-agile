# Sprint 1 review

- Date: 2026-11-12
- Product Owner: Stanley
- Sprint goal: turn the 12 Must stories into accepted, estimated requirements, and draft the use case diagram
- Result: goal met. 12 of 12 stories accepted, 33 of 33 points. The use case diagram (#31) and the class, sequence and activity diagrams (#32) are merged.
- Beyond the goal: a working prototype of all 12 stories (#33).

## Results

Each acceptance criterion has a test named after it in `tests/`. CI ran them on macOS and Linux for #33.

| Story | Points | Result | Evidence |
| --- | --- | --- | --- |
| S01 Shared values in a module (#6) | 2 | Accepted | `test_one_value_reaches_every_output_that_uses_it`, `test_syntax_error_names_file_and_line_writes_nothing_exits_3` |
| S02 Built-in templates (#7) | 3 | Accepted | `BuiltInTemplateTest`: bash, zsh and fish output is valid syntax; Alacritty gets colors and font |
| S05 Target paths per OS (#10) | 2 | Accepted | `test_uses_the_path_for_the_current_os`, `test_output_without_path_for_this_os_is_skipped_and_reported` |
| S06 Manifest validation (#11) | 3 | Accepted | `test_target_outside_home_is_rejected`, `test_two_outputs_with_the_same_target_are_rejected` |
| S07 Profiles by OS and Host ID (#12) | 3 | Accepted with change | `test_host_id_enables_its_outputs`, `test_os_profile_does_not_match_other_os`, `test_no_match_uses_default_and_says_so`. Changed from hostname to Host ID during the sprint |
| S09 Preview changes (#14) | 3 | Accepted | `test_preview_shows_diff_and_writes_nothing`, `test_nothing_to_apply_exits_0` |
| S11 Apply outputs (#16) | 3 | Accepted | `test_apply_writes_regular_files_and_summarises`, `test_identical_file_is_not_rewritten` |
| S12 Roll back a failed apply (#17) | 5 | Accepted | `test_failed_write_restores_everything_and_exits_1`, `test_rollback_removes_new_files` |
| S13 Detect hand edits (#19) | 5 | Accepted | `test_hand_edit_is_kept_and_reported_others_still_apply`, `test_unedited_output_is_not_drifted` |
| S19 Never wait for input (#25) | 1 | Accepted | `test_never_reads_stdin` |
| S20 Documented exit codes (#26) | 1 | Accepted with change | Exit codes are checked across the tests. Exit code 1 for a failed preflight was added at the start of Sprint 2 (`test_preflight_stops_before_writing`) |
| S23 Back up existing files (#18) | 2 | Accepted | `test_allowed_take_over_backs_up_first`, `test_not_allowed_take_over_skips_and_exits_2` |

Rejected: none.

## Changes found during the sprint

All are listed in `docs/decisions.md`.

- S07: the hostname became a fixed Host ID, after the AI-agent team's ADR-0011.
- S20: drawing the activity diagram showed it had no exit code for a failed preflight. The PO chose exit code 1.

## Known limits

- Windows paths are in the manifest but not tested.

## Velocity

Planned 33 points, done 33 points. Sprint 2 commits 21 points.
