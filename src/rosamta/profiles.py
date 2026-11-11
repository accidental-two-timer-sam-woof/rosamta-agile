"""Profiles choose which outputs this machine enables (S07, S08).

profiles.toml:

    [default]                 # applies to every machine
    outputs = ["bash", "zsh"]

    [[profile]]
    name = "work-mac"
    os = ["macos"]            # optional
    host_ids = ["work-laptop"]  # optional, matched against the fixed Host ID
    tags = ["gui"]            # optional, any of these tags
    outputs = ["alacritty"]

A profile matches when every criterion it lists matches. The enabled outputs are
the union of the default profile and every matching profile.
"""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from rosamta import paths
from rosamta.errors import ConfigError


@dataclass
class Machine:
    os: str
    host_id: str
    tags: list[str] = field(default_factory=list)


@dataclass
class Selection:
    enabled: dict[str, list[str]]   # output name -> profiles that enabled it
    matched: list[str]              # matching profiles other than default


def select_outputs(config: Path, machine: Machine, all_outputs: list[str]) -> Selection:
    path = config / "profiles.toml"
    try:
        text = paths.read_text(path)
    except FileNotFoundError:
        return Selection({name: ["default"] for name in all_outputs}, [])
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as err:
        raise ConfigError(f"{path}: {err}", path) from None

    enabled: dict[str, list[str]] = {}

    def enable(names, profile):
        for name in names:
            if name not in all_outputs:
                raise ConfigError(f"{path}: profile {profile} enables unknown output {name}; "
                                  "add it to manifest.toml or remove it from the profile", path)
            enabled.setdefault(name, []).append(profile)

    enable(data.get("default", {}).get("outputs", []), "default")
    matched = []
    for profile in data.get("profile", []):
        name = profile.get("name", "?")
        if "os" in profile and machine.os not in profile["os"]:
            continue
        if "host_ids" in profile and machine.host_id not in profile["host_ids"]:
            continue
        if "tags" in profile and not set(profile["tags"]) & set(machine.tags):
            continue
        matched.append(name)
        enable(profile.get("outputs", []), name)
    return Selection(enabled, matched)
