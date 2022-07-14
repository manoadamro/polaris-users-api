"""
Build make/tox documentation for README file.

Usage: python make-targets.py <readme filename>

For each <markdown-make makefile toxfile> tag in the input file, replace the text from <markdown-make ...> to
</markdown-make> with a generate list of makefile and toxfile targets. The toxfile is optional, makefile is required.

Targets that are documented are those from the makefile with a '##' comment. e.g.

clean:   ## Remove tox and pyenv virtual environments.

Extracts documented make targets from Makefile.
"""
import argparse
import re
import sys
from pathlib import Path
from typing import Generator, List, Optional, Sequence, Tuple

VERBOSE = False


def make_targets(makefile: str) -> Generator[Tuple[str, str], None, None]:
    target, description = "", ""
    with open(makefile) as f:
        for line in f:
            line = line.strip()
            if target and description:
                if line.startswith("## "):
                    description += " " + line[2:].strip()
                else:
                    yield target, description
                    target, description = "", ""

            parts = line.split(":", 1)
            if len(parts) == 2 and parts[1].strip().startswith("## "):
                target, description = parts[0].strip(), parts[1].strip()[3:]
    if target and description:
        yield target, description


def tox_targets(tox_content: List[str]) -> Generator[Tuple[str, str], None, None]:
    env = ""
    desc = ""

    for line in tox_content:
        if env and desc:
            if line.startswith(" "):
                desc += " " + line.strip()
                continue
            else:
                yield env, desc
                env, desc = "", ""

        if m := re.match(r"\[testenv:(?P<env>.*)]", line):
            env = m.group("env")
        if m := re.match(r"description\s*=\s*(?P<description>.+)", line):
            desc = m.group("description")
    if env and desc:
        yield env, desc


def tox_envlist(tox_content: List[str]) -> List[str]:
    for line in tox_content:
        if m := re.match("envlist\s*=\s*(?P<envlist>.+)", line):
            return m.group("envlist").split(",")
    return []


def replace_tag(m: re.Match) -> str:
    makefile: str
    toxfile: Optional[str]
    makefile, toxfile, start_mark, end_mark = m.group(
        "makefile", "toxfile", "start_mark", "end_mark"
    )
    if VERBOSE:
        print(f"Found tag {makefile} {toxfile}")
    targets = [
        (target, f"`make {target}`", description)
        for target, description in make_targets(makefile)
    ]

    if toxfile:
        tox_content = Path(toxfile).read_text().split("\n")
        envlist = tox_envlist(tox_content)
        if envlist:
            targets += [
                (
                    "",
                    "`tox`",
                    f"Running `make test` or tox with no arguments runs `tox -e "
                    f"{','.join(envlist)}`",
                ),
            ]
        targets += [
            (target, f"`make {target}` (or `tox -e {target}`)", description)
            for target, description in tox_targets(tox_content)
            if "--" not in description
        ] + [
            (target, f"`tox -e {target}`", description)
            for target, description in tox_targets(tox_content)
            if "--" in description
        ]

    if VERBOSE:
        for key, target, description in sorted(targets):
            print(f"{target}: {description}")

    return (
        start_mark
        + "\n"
        + "".join(
            f"{target} : {description}\n\n"
            for key, target, description in sorted(targets)
        )
        + end_mark
    )


def update_tag(content: str) -> str:
    pattern = (
        r"(?P<start_mark>\<!--\s*markdown-make\s+(?P<makefile>[^ ]+)(\s+(?P<toxfile>[^ ]+))?\s*--\>)(?P<body>.*?)("
        r"?P<end_mark>\<!--\s*/markdown-make\s*--\>)"
    )
    new_content = re.sub(pattern, replace_tag, content, flags=re.DOTALL)
    return new_content


def main(argv: Optional[Sequence[str]] = None) -> int:
    global VERBOSE
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Markdown file with `markdown-make` tag")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show progress")
    parser.add_argument(
        "--dry-run", "-n", action="store_true", help="Don't update the readme"
    )
    args = parser.parse_args(argv)
    VERBOSE = args.verbose

    md_file = Path(args.filename)
    tmp_out = md_file.with_suffix(".$$$")
    try:
        content = md_file.read_text()
        new_content = update_tag(content)

        if new_content != content:
            if args.dry_run:
                print("Dry-run - not modifying file")
            else:
                tmp_out.write_text(new_content)
                tmp_out.replace(md_file)
            print(f"{md_file} targets updated")
        else:
            print(f"{md_file} did not change")
    finally:
        tmp_out.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
