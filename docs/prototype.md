# Prototype


A working prototype of rosamta lives in `src/rosamta`. It covers every Must story and most Should stories. Needs Python 3.11 or newer and nothing else.

```sh
pip install -e .                  # or run without installing: PYTHONPATH=src python3 -m rosamta ...
rosamta --config example preview  # show what would change, write nothing
rosamta --config example apply    # write the generated files
rosamta init example --tag gui    # remember the config folder and this machine's tags, then apply
rosamta query theme               # which outputs use the theme module
rosamta --json apply              # one JSON document, for scripts and AI assistants
```

The `example/` folder is a complete config: modules (`shellrc`, `theme`, `font`), a manifest with four outputs (bash, zsh, fish, Alacritty), and profiles.

| Exit code | Meaning |
| --- | --- |
| 0 | every output written or unchanged |
| 1 | something failed; nothing was left half-written |
| 2 | finished, but some outputs were skipped (hand edits, or a file rosamta may not take over) |
| 3 | invalid configuration; nothing written |

Run the tests (one test file per epic, each test named after an acceptance criterion):

```sh
cd tests && PYTHONPATH=../src python3 -m unittest -v
```
