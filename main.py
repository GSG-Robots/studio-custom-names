"""
Studio Custom Names is a program to change the names of the parts in Studio 2.0.
Copyright (C) 2024 GSG-Robots & J0J0HA aka. JoJoJux

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import re
import pathlib
import ctypes
import glob
import shutil
import sys


TERMINAL_WIDTH = shutil.get_terminal_size().columns

def print_limited_width(text, end="\n"):
    if len(text) > TERMINAL_WIDTH:
        print(text[:TERMINAL_WIDTH - 6 - len(end)] + " [...]", end=end)
    else:
        print(text, end=end)

def print_license():
    with open("LICENSE", "r", encoding="utf-8") as f:
        print(f.read())
    pause_and_exit(0)


def input_yn(question):
    do = input(f"{question} (y/n) ")
    if do == ":license":
        print_license()
    if do == ":exit":
        sys.exit(0)
    if do.lower() == "y":
        return True
    elif do.lower() == "n":
        return False
    else:
        return None


def input_str(question):
    do = input(f"{question} ")
    if do == ":license":
        print_license()
    if do == ":exit":
        sys.exit(0)
    return do


def pause_and_exit(code=0):
    input("Press Enter to exit...")
    sys.exit(code)


def find_studio():
    studio_root = None
    if not sys.argv[1:]:
        known_paths = [
            (
                pathlib.Path(r"C:\Program Files\Studio 2.0"),
                "Studio 2.0 (Default Directory)",
            ),
            (
                pathlib.Path(r"C:\Program Files (x86)\Studio 2.0"),
                "Studio 2.0 32bit (Default Directory)",
            ),
            (
                pathlib.Path(r"C:\Program Files\Studio 2.0 EarlyAccess"),
                "Studio 2.0 EarlyAccess (Default Directory)",
            ),
            (
                pathlib.Path(r"C:\Program Files (x86)\Studio 2.0 EarlyAccess"),
                "Studio 2.0 EarlyAccess 32bit (Default Directory)",
            ),
        ]

        print("Please select the Studio 2.0 installation you want to use:\n")
        options = [
            x
            for x in known_paths
            if os.path.exists(x[0]) and os.path.exists(x[0] / "data")
        ]
        for i, x in enumerate(options):
            print(f"{i + 1}: {x[1]} [{x[0]}]")

        choice = input_str(
            "\n\nEnter the number or direct path of the installation you want to use:"
        )

        if not choice:
            print("Exiting.")
            pause_and_exit(0)
        if not choice.isdigit():
            if os.path.exists(pathlib.Path(choice)):
                studio_root = pathlib.Path(choice)
            else:
                print("That path does not exist. Exiting.")
                pause_and_exit(1)
        elif int(choice) < 1 or int(choice) > len(options):
            print("That was not an option. Exiting.")
            pause_and_exit(1)
        else:
            studio_root = options[int(choice) - 1][0]
        if not os.path.exists(studio_root / "data"):
            print("The path you provided is not a Studio 2.0 installation. Exiting.")
            pause_and_exit(1)
    else:
        path = " ".join(sys.argv[1:])
        studio_root = pathlib.Path(path)
        if not os.path.exists(studio_root):
            print("The path you provided does not exist. Exiting.")
            pause_and_exit(1)
        if not os.path.exists(studio_root / "data"):
            print("The path you provided is not a Studio 2.0 installation. Exiting.")
            pause_and_exit(1)
    return studio_root


def elevate():
    if ctypes.windll.shell32.IsUserAnAdmin():
        return
    code = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    if not code >= 32:
        print("Failed to elevate. Try running the program as admin. Exiting.")
        pause_and_exit(1)
    sys.exit(0)


elevate()

print(
    """
----------
Studio Custom Names - Copyright (C) 2024  GSG-Robots & J0J0HA aka. JoJoJux
This program comes with ABSOLUTELY NO WARRANTY; for details see the LICENSE-file.
This is free software, and you are welcome to redistribute it
under certain conditions; for details see the LICENSE-file.
You can also type ":license" to see the license.
----------
Type ":exit" at any prompt to exit.
----------
"""
)

PROGRAM_ROOT = pathlib.Path(__file__).parent.absolute()
STUDIO_ROOT = find_studio()
CHANGES_FILE = PROGRAM_ROOT / "changes.log"
ORIGINAL_FILE = STUDIO_ROOT / "data" / "studio-costom-names.ORIGINAL.txt"
COPY_FILE = STUDIO_ROOT / "data" / "studio-costom-names.COPY.txt"
TARGET_FILE = STUDIO_ROOT / "data" / "StudioPartDefinition2.txt"

LOG_FILE = open(CHANGES_FILE, "w", encoding="utf-8")

def _load_id_rules(file_path):
    with open(file_path, "r", errors="replace", encoding="utf-8") as f:
        mapping_raw = f.read()
        mapping = {
            x[0]: x[1]
            for x in (
                y.split(" => ")
                for y in mapping_raw.split("\n")
                if y.strip() != "" and not y.startswith("#")
            )
        }
    return mapping


def _load_regex_rules(file_path):
    with open(file_path, "r", errors="replace", encoding="utf-8") as f:
        mapping_raw = f.read()
        mapping = {
            re.compile(x[0]): x[1]
            for x in (
                y.split(" => ")
                for y in mapping_raw.split("\n")
                if y.strip() != "" and not y.startswith("#")
            )
        }
    return mapping


def load_rules():
    print("Loading rules...")
    id_rules, regex_rules = {}, {}
    for file in glob.glob(str(PROGRAM_ROOT / "rules" / "*.id.rules")):
        id_rules.update(_load_id_rules(file))
    for file in glob.glob(str(PROGRAM_ROOT / "rules" / "*.regex.rules")):
        regex_rules.update(_load_regex_rules(file))
    print(f"Done. Loaded {len(id_rules)} id rules and {len(regex_rules)} regex rules.")
    return id_rules, regex_rules


def check_was_updated():
    if not os.path.exists(COPY_FILE):
        return
    with open(COPY_FILE, "r", errors="replace", encoding="utf-8") as f:
        copy = f.read()
    with open(TARGET_FILE, "r", errors="replace", encoding="utf-8") as f:
        target = f.read()
    if copy == target:
        return
    print(
        "It seems like the Parts definition was manipulated by another program. This most likely happened due to a Studio update."
    )
    print('-> If it was not a Studio update, choose "n".')
    print('-> If it was a Studio update, choose "y".')
    print(
        "NOTE: If you choose the wrong option, it may lead to problems only fixable via a Studio reinstall (or maybe update)."
    )
    do = input_yn("Do you want to use the updated version as base?")
    if do is True:
        shutil.copyfile(str(TARGET_FILE), str(ORIGINAL_FILE))
    elif do is False:
        print("Continuing...")
    else:
        print("Aborting.")
        pause_and_exit(1)


def ensure_backup_original():
    if os.path.exists(ORIGINAL_FILE):
        return
    print("Setting up StudioCustomNames initially for this Studio instance...")
    shutil.copyfile(str(TARGET_FILE), str(ORIGINAL_FILE))


def get_part_definition():
    print("Reading base file...")
    with open(
        ORIGINAL_FILE,
        "r",
        errors="replace",
        encoding="utf-8",
    ) as f:
        content = f.read()
    if not content.startswith("Studio "):
        print("Data corrupted or not a Studio 2.0 installation. Exiting.")
        pause_and_exit(1)
    else:
        content = content[len("Studio ") :]
    lines = content.split("\n")
    table_ = [re.split(r"\t", line) for line in lines]

    return table_


def store_part_definition(table_):
    new_content = "Studio " + "\n".join(["\t".join(row) for row in table_])
    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    shutil.copyfile(str(TARGET_FILE), str(COPY_FILE))


def generate_regex_result(s):
    return lambda m: s.format(*m.groups())


def apply_rules(table, id_rules, regex_rules):
    print("Applying rules...")
    count = 0
    for row in table:
        if len(row) < 7:
            continue
        name = row[6]
        part_id = row[2]
        if part_id in id_rules:
            name = id_rules[part_id]
        for k, v in regex_rules.items():
            name = re.sub(k, generate_regex_result(v), name)
        if name != row[6]:
            count += 1
            text = f"Applying: {part_id:<8} {row[6]:<80} => {name:>40}"
            print(text, file=LOGFILE)
            print_limited_width(text, end="\r")
        row[6] = name
    text = f"Done. Changed {count} names."
    print(text + " " * (TERMINAL_WIDTH - len(text) + 1))


#######

ensure_backup_original()

check_was_updated()

id_rules, regex_rules = load_rules()

table = get_part_definition()

apply_rules(table, id_rules, regex_rules)

store_part_definition(table)

pause_and_exit(0)
