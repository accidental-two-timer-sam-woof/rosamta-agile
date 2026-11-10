# Contributing

This project follows an Agile process. User stories and sprints are tracked in GitHub Projects, and every document reaches `main` through a pull request. Please read this guide before opening a PR.

## Workflow

1. Move the story to **In Progress** on the board and create a branch from the latest `main`
2. Do the work on the branch. Each commit is one finished task
3. Push the branch and open a PR using the template
4. Address review comments, then clean up the commit history
5. Merge into `main` with **rebase merge** and delete the branch

## Branch names

```
<type>/<short-description>
```

- `type` is the same as the commit type (see [Types](#types))
- The description is English, lowercase, joined with `-`
- When the work belongs to a story, put the issue number first and write `Closes #<number>` in the PR description, so the board links to the history

```
docs/12-profile-stories
docs/uml-use-case
chore/issue-templates
```

## Commits

### One commit is one finished task

Every commit on `main` should make sense on its own.

- No `wip`, `tmp` or `fix typo` commits. Squash them before merging (see [Cleaning up history](#cleaning-up-history))
- One commit does one thing. If the subject needs "and", it is probably two commits
- A docs commit is a complete change, such as a finished section or a related set of stories

### Format

We use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
<type>(<scope>): <subject>

<body>
```

- Subject: under 50 characters if possible, 72 at most, lowercase, no trailing period
- Body: optional. Explain **why**, not what. Wrap at 72 characters

Examples:

```
docs(stories): add acceptance criteria for profile matching
docs(uml): add use case diagram
chore: add user story issue template
```

### Types

| type | Use for |
| --- | --- |
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation, stories, records |
| `refactor` | Code change without behavior change |
| `test` | Tests |
| `build` | Build system, dependencies |
| `chore` | Other housekeeping, such as config and repo structure |

### Scopes

Optional. Use them to mark which document changed:

| scope | Path |
| --- | --- |
| `vision` | `docs/vision.md` |
| `stories` | User story documents |
| `ai-log` | `docs/ai-log` |
| `daily` | `daily` |
| `sprint` | `sprints` |
| `uml` | `uml` |

## Pull requests

- Rebase on the latest `main` before opening a PR. Do not merge `main` into your branch
- Fill in the PR template and delete sections you don't need
- At least one other member must approve before merging

### Cleaning up history

We use rebase merge, so every commit on the branch lands on `main` as is. Clean up first:

```sh
git fetch origin
git rebase -i --autosquash origin/main
git push --force-with-lease
```

Use `--force-with-lease`, never `--force`.

## Writing style

- Documents are written in English
- No emoji in documents or commit messages
