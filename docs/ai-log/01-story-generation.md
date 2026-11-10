# 01 Story generation

- Date: 2026-11-10
- Who: Stanley
- Tool and model: Claude Code (Claude Opus 5.5)
- Purpose: draft the first epics and user stories for the product backlog, with acceptance criteria and suggested story points

## Prompt

```text
You are helping a student Agile team. Product: "rosamta", a cross-platform dotfile manager. Settings shared by many programs (colors, fonts, shell env) live in modules; templates turn module values into each program's config format; a manifest declares outputs and target paths; profiles choose which outputs each machine enables.

Scope for v1: modules, templates (built-in and overridable), manifest, profiles (by OS, hostname, tags), preview and preflight, apply with rollback, drift detection (keep user edits by default), cleanup of old outputs, query (module to outputs), init on a new machine, and script/AI-assistant-friendly output (exit codes, no prompts).
Out of scope: symlinks, git sync, secrets management, writing outside home, installing packages.

Users: regular user, advanced user who writes templates, scripts without a terminal, someone using rosamta through an AI assistant.

Write 3 to 4 epics, then 15 to 25 user stories. Each story: "As a <user>, I want <goal> so that <benefit>", 2 to 3 Given/When/Then acceptance criteria, and a suggested story point (1, 2, 3, 5, 8). Each story must be small enough for one day of work. Follow INVEST. Do not invent features outside the scope above.
```

## AI output (verbatim)

### Notes from the AI

- User names follow `docs/vision.md`: regular user, advanced user, script user, AI assistant user.
- Command names and flags (`rosamta preview`, `--json`, `--overwrite`) are placeholders to make the criteria testable. The team should pick the real names.
- No story is 8 points. An 8 would not fit in one day, so it should be split before it enters a sprint. The one 5-point story (S12) is the first candidate to split if the team estimates it higher.
- Known dependencies (the "I" in INVEST is not perfect): S14 builds on S13, and S17 reuses the lookup from S16. Each one can still be demonstrated on its own.

### Epics

| ID | Epic | Goal |
| --- | --- | --- |
| E1 | Describe my setup | Modules, templates, manifest and profiles describe what rosamta generates and where |
| E2 | Apply safely | Preview, preflight and apply with rollback, so a change never leaves files half-written |
| E3 | Keep outputs in sync | Drift detection, cleanup and query keep generated files trustworthy over time |
| E4 | New machines and automation | Init on a new machine, plus output that scripts and AI assistants can rely on |

### E1 Describe my setup

#### S01 Shared values in a module

As a regular user, I want to keep shared settings such as colors and fonts in one module file so that I change a value in one place instead of in every program's config.

- Given a module that sets `colors.background`, When rosamta generates outputs, Then every output whose template uses `colors.background` contains that value.
- Given a module file with a syntax error, When I run any rosamta command, Then rosamta reports the file and line of the error, writes nothing, and exits with a non-zero code.

Suggested points: 3

#### S02 Built-in templates

As a regular user, I want built-in templates for common programs so that I get working config files without writing any templates myself.

- Given a module with colors and fonts and a manifest entry that uses a built-in template, When rosamta generates that output, Then the content is in that program's own config format.
- Given a built-in template that needs a module value I have not set, When rosamta generates the output, Then it reports the template name and the missing key, and does not write that output.

Suggested points: 3

#### S03 Override a built-in template

As an advanced user, I want to override a single built-in template with my own file so that I can change one program's generated config without changing rosamta itself.

- Given a user template with the same name as a built-in template, When rosamta generates that output, Then it uses my template instead of the built-in one.
- Given I delete my override file, When rosamta generates the output again, Then it falls back to the built-in template.
- Given my override template fails to render, When rosamta generates outputs, Then the error names my template file and line, not the built-in one.

Suggested points: 3

#### S04 Template for a new program

As an advanced user, I want to write a template for a program rosamta does not cover so that this program also follows my module values.

- Given a new template and a manifest entry that points to it, When rosamta generates outputs, Then the new output is generated with values from my modules.
- Given I change a module value used by my new template, When rosamta generates outputs again, Then the new output reflects the changed value.

Suggested points: 2

#### S05 Target paths per operating system

As a regular user, I want the manifest to declare each output's target path per operating system so that the same setup works on macOS, Linux and Windows.

- Given an output with different target paths for macOS and Linux, When rosamta runs on Linux, Then it uses the Linux path.
- Given an output with no target path for the current operating system, When rosamta runs, Then that output is skipped and reported as not available on this platform.

Suggested points: 3

#### S06 Manifest validation

As a regular user, I want rosamta to reject invalid manifest entries so that a typo can never write a file somewhere unexpected.

- Given a manifest entry whose target path resolves outside my home directory, When rosamta loads the manifest, Then it reports the entry, writes nothing, and exits with a non-zero code.
- Given two manifest entries with the same target path, When rosamta loads the manifest, Then it reports both entries as a conflict and writes nothing.

Suggested points: 2

#### S07 Profiles by operating system and hostname

As a regular user, I want profiles that enable outputs by operating system and hostname so that each machine gets only the configs it needs.

- Given a profile for hostname `work-laptop` that enables the terminal output, When rosamta runs on `work-laptop`, Then the terminal output is enabled.
- Given a profile for Linux only, When rosamta runs on macOS, Then the outputs from that profile are not enabled.
- Given no profile matches this machine, When rosamta runs, Then only outputs enabled for all machines are used, and rosamta says no profile matched.

Suggested points: 3

#### S08 Profiles by tag

As a regular user, I want to tag a machine (for example `gui` or `server`) and enable outputs by tag so that I do not have to list every hostname in my profiles.

- Given this machine is tagged `server` and a profile enables outputs for tag `gui`, When rosamta runs, Then the `gui` outputs are not enabled.
- Given several profiles match this machine, When rosamta runs, Then the enabled outputs are the union of all matching profiles, and each output shows which profile enabled it.

Suggested points: 3

### E2 Apply safely

#### S09 Preview changes

As a regular user, I want to preview what will change before anything is written so that I can check the result first.

- Given I changed a module value, When I run `rosamta preview`, Then it shows a diff for each output that would change and writes no files.
- Given nothing would change, When I run `rosamta preview`, Then it says there is nothing to apply and exits with code 0.

Suggested points: 3

#### S10 Preflight checks

As a regular user, I want rosamta to run preflight checks before writing so that an apply does not fail halfway because of a problem it could have found first.

- Given a target directory that is not writable, When preflight runs, Then it reports the path and apply stops before writing any file.
- Given a module refers to a font that is not installed, When preflight runs, Then it reports the font as missing as a warning, and rosamta does not try to install it.

Suggested points: 3

#### S11 Apply outputs

As a regular user, I want to apply the generated outputs to their target paths so that my programs start using the new settings.

- Given preflight passes, When I run `rosamta apply`, Then each enabled output is written as a regular file at its target path, and a summary lists written, unchanged and skipped outputs.
- Given an output whose generated content is identical to the file on disk, When I run `rosamta apply`, Then that file is not rewritten and is listed as unchanged.

Suggested points: 3

#### S12 Roll back a failed apply

As a regular user, I want a failed apply to undo every file it already changed so that my machine is never left with half the configs updated.

- Given three outputs to write and the second write fails, When apply stops, Then the first file is restored to its previous content, the third is not touched, and rosamta exits with a non-zero code.
- Given apply created a new file before the failure, When rollback runs, Then that new file is removed.

Suggested points: 5

### E3 Keep outputs in sync

#### S13 Detect hand edits (drift)

As a regular user, I want rosamta to notice when I have edited a generated file by hand so that my edits are never overwritten without me knowing.

- Given I edited an output after the last apply, When I run `rosamta apply`, Then that file is kept as it is, reported as drifted, and the other outputs are applied normally.
- Given I did not edit an output, When I run `rosamta apply`, Then it is updated as usual and not reported as drifted.

Suggested points: 3

#### S14 Choose to overwrite a drifted file

As a regular user, I want to explicitly overwrite a drifted output so that I can take rosamta's version when I decide my hand edit is no longer needed.

- Given a drifted output, When I run `rosamta preview`, Then it shows the difference between my edited file and the newly generated content.
- Given a drifted output, When I run `rosamta apply --overwrite <output>`, Then that file is replaced with the generated content and is no longer reported as drifted.

Suggested points: 2

#### S15 Clean up old outputs

As a regular user, I want rosamta to remove files it generated that are no longer enabled so that old configs do not pile up in my home directory.

- Given an output that is no longer enabled and whose file is unchanged since rosamta wrote it, When I run cleanup, Then the file is deleted and listed as removed.
- Given an output that is no longer enabled but whose file I edited, When I run cleanup, Then the file is kept and listed as kept because of user edits.
- Given a file that rosamta never wrote, When I run cleanup, Then rosamta does not touch it.

Suggested points: 3

#### S16 Query which outputs use a module

As a regular user, I want to ask which outputs use a module so that I know what will change before I edit it.

- Given the `colors` module is used by three enabled outputs, When I run `rosamta query colors`, Then it lists those three outputs with their target paths.
- Given a module name that does not exist, When I run `rosamta query` with it, Then it reports that the module is unknown and exits with a non-zero code.

Suggested points: 2

#### S17 Query which modules feed an output

As an advanced user, I want to ask which modules an output uses so that I can find where a value in a generated file comes from.

- Given an output whose template uses the `colors` and `fonts` modules, When I query that output, Then it lists `colors` and `fonts`.
- Given an output name that is not in the manifest, When I query it, Then it reports that the output is unknown and exits with a non-zero code.

Suggested points: 2

### E4 New machines and automation

#### S18 Initialize a new machine

As a regular user, I want to set up rosamta on a new machine with one command so that I can start using my existing modules quickly.

- Given my rosamta config folder is already on the new machine, When I run `rosamta init`, Then rosamta detects the operating system and hostname, records them, and lists the outputs that would be enabled, without writing any output files.
- Given init has already run on this machine, When I run `rosamta init` again, Then nothing changes and it exits with code 0.

Suggested points: 3

#### S19 Never wait for input

As a script user, I want rosamta to never prompt for input so that a scheduled run can never hang.

- Given rosamta runs without a terminal, When it meets a drifted output, Then it keeps the user's edit, reports it, and continues without asking.
- Given rosamta runs without a terminal, When any command needs a decision it cannot make safely, Then it stops with an error and a non-zero exit code instead of waiting.

Suggested points: 2

#### S20 Documented exit codes

As a script user, I want distinct, documented exit codes so that my script can tell success, partial success and failure apart.

- Given apply writes every output, When it finishes, Then it exits with code 0.
- Given apply finishes but skipped some outputs because of drift, When it finishes, Then it exits with a code that differs from both success and failure.
- Given the manifest or a module is invalid, When any command runs, Then it exits with a configuration error code listed in the documentation.

Suggested points: 2

#### S21 Machine-readable output

As an AI assistant user, I want a JSON output option for preview, apply and query so that my assistant can read the result without parsing human text.

- Given I run `rosamta apply --json`, When it finishes, Then standard output is a single valid JSON document listing each output's path and status, with no color codes.
- Given a command fails with `--json`, When it exits, Then the JSON includes an error code, the file involved and a message.

Suggested points: 3

#### S22 Actionable error messages

As an AI assistant user, I want each error to say what failed, where, and what to change so that the assistant can fix my files without guessing.

- Given a template uses a module key that is not set, When rosamta reports the error, Then the message names the template, the line, the missing key and the module file where it should be set.
- Given any command, When it reports errors, Then errors go to standard error and results go to standard output.

Suggested points: 2

### Summary

| Epic | Stories | Suggested points |
| --- | --- | --- |
| E1 Describe my setup | S01 to S08 | 22 |
| E2 Apply safely | S09 to S12 | 14 |
| E3 Keep outputs in sync | S13 to S17 | 12 |
| E4 New machines and automation | S18 to S22 | 12 |
| Total | 22 stories | 60 |

## Accepted and rejected

Filled in by the Product Owner after review.

| Item | Decision | Reason | Approved by |
| --- | --- | --- | --- |
|  |  |  |  |

## Where the AI was wrong

(fill in after review)

## Time saved or lost

(fill in after review)
