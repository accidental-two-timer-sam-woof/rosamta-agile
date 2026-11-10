# Product vision

> Written by the Product Owner (Stanley), drafted with AI help and edited by hand. See `docs/ai-log/00-repo-setup.md`.

## Problem

Settings such as colors, fonts, shell variables and aliases are copied into the config files of many programs and many machines. Changing one value means editing many files by hand, and the copies drift apart over time.

## Target users

- **Regular user:** works on the command line and edits one module file to change a setting everywhere.
- **Advanced user:** writes their own modules and templates for programs rosamta does not cover.
- **Script user:** runs rosamta from scripts or schedulers with no terminal, so it must never wait for input and must report results through exit codes.
- **AI assistant user:** asks an AI assistant to change settings. rosamta's commands, output and errors must be clear enough that the assistant can use them without guessing.

## First release scope (MVP)

- One module generates the config files of several programs
- Built-in modules and templates, with per-template overrides
- A manifest that declares every output and its target path per platform
- Profiles that enable outputs by operating system, hostname or tag
- Preview and preflight checks before anything is written
- Apply with automatic rollback on error
- Drift detection: user edits to outputs are kept by default
- Cleanup of old outputs that were not modified
- Query: which module feeds which output, and the reverse
- One-command initialization on a new machine

## Out of scope

- Symlinks (rosamta only writes regular files)
- Git sync (pull, push, merge conflicts)
- Secrets management or encryption
- Writing outside the home directory
- Installing software packages or fonts (rosamta only reports what is missing)
