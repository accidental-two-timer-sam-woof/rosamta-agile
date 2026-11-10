"""Which outputs use a module, and which modules feed an output (S16, S17)."""

from pathlib import Path

from rosamta import manifest, paths
from rosamta.errors import ConfigError
from rosamta.module import load_modules
from rosamta.templates import find_template


def query(config: Path, name: str) -> list[str]:
    modules = load_modules(config)
    outputs = manifest.load_manifest(config)
    os_name = paths.current_os()
    if name in modules:
        lines = []
        for output in outputs:
            if name in find_template(config, output.template).modules_used():
                target = output.target_for(os_name)
                lines.append(f"{output.name}\t{paths.display(target) if target else '(not on this OS)'}")
        return lines
    for output in outputs:
        if output.name == name:
            return find_template(config, output.template).modules_used()
    raise ConfigError(f"{name}: not a module or an output")
