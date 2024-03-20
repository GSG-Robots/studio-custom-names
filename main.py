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
import sys
import time


config_root = pathlib.Path(__file__).parent.absolute()
elev_proxy_file = config_root / "elevated_stdout.txt"
log_file = config_root / "log.txt"

regex_rules = {}
id_rules = {}


print(
    """
----------
Studio Custom Names - Copyright (C) 2024  GSG-Robots & J0J0HA aka. JoJoJux
This program comes with ABSOLUTELY NO WARRANTY; for details see the LICENSE-file.
This is free software, and you are welcome to redistribute it
under certain conditions; for details see the LICENSE-file.

If you get prompted to input a path, you can type "license" to view the license.
----------
"""
)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return os.getuid() == 0


def follow_until_closed(path: pathlib.Path):
    pos = 0
    while True:
        with open(path, "r", errors="replace", encoding="utf-8") as file:
            file.seek(pos)
            line = file.readline()
            pos = file.tell()
        try:
            os.rename(elev_proxy_file, elev_proxy_file)
            break
        except PermissionError:
            pass
        if not line:
            time.sleep(0.1)
            continue
        yield line


def elevate(selected_path):
    if not is_admin():
        print(
            "\nYou are not running as Administrator. Elevating...\n\nPlease accept the UAC prompt."
        )
        if " " in str(config_root):
            print(
                "The path to this program contains spaces. This is not supported. Run this program from a path without spaces, or directly as Administrator. Exiting."
            )
            sys.exit(1)
        if os.path.exists(elev_proxy_file):
            os.remove(elev_proxy_file)
        code = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            "cmd",
            f"/C \"{sys.executable}\" {str(config_root / 'main.py')} {selected_path} >> {elev_proxy_file}",
            0,
        )
        success = code >= 32
        if not success:
            print("Failed to elevate. Try running the program as admin. Exiting.")
            sys.exit(1)
        while not os.path.exists(elev_proxy_file):
            time.sleep(0.1)
        try:
            for line in follow_until_closed(elev_proxy_file):
                print(line, end="")
        finally:
            os.remove(elev_proxy_file)
        sys.exit(0)


def exists(path: pathlib.Path):
    return os.path.exists(str(path))


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
    id_rules.update(mapping)


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
    regex_rules.update(mapping)


def load_rules():
    for file in glob.glob(str(config_root / "rules" / "*.id.rules")):
        _load_id_rules(file)
    for file in glob.glob(str(config_root / "rules" / "*.regex.rules")):
        _load_regex_rules(file)


def ensure_backup_original():
    if not os.path.exists(str(studio_data_root / "StudioPartDefinition2.txt.original")):
        with open(
            str(studio_data_root / "StudioPartDefinition2.txt"),
            "r",
            errors="replace",
            encoding="utf-8",
        ) as f:
            file_content = f.read()
        with open(
            str(studio_data_root / "StudioPartDefinition2.txt.original"),
            "w",
            errors="replace",
            encoding="utf-8",
        ) as f:
            f.write(file_content)


def get_part_definition():
    with open(
        str(studio_data_root / "StudioPartDefinition2.txt.original"),
        "r",
        errors="replace",
        encoding="utf-8",
    ) as f:
        content = f.read()
    if not content.startswith("Studio "):
        raise ValueError
    else:
        content = content[len("Studio ") :]
    lines = content.split("\n")
    table_ = [re.split(r"\t", line) for line in lines]

    return table_


def store_part_definition(table_):
    new_content = "Studio " + "\n".join(["\t".join(row) for row in table_])
    with open(
        str(studio_data_root / "StudioPartDefinition2.txt"),
        "w",
        errors="replace",
        encoding="utf-8",
    ) as f:
        f.write(new_content)


def generate_regex_result(s):
    return lambda m: s.format(*m.groups())


#########

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
    options = [x for x in known_paths if exists(x[0])]
    for i, x in enumerate(options):
        print(f"{i + 1}: {x[1]} [{x[0]}]")

    choice = input(
        "\n\nEnter the number or direct path of the installation you want to use: "
    )

    if choice.lower() == "license":
        with open(
            config_root / "LICENSE", "r", errors="replace", encoding="utf-8"
        ) as f:
            print(f.read())
        sys.exit(0)

    if not choice:
        print("Exiting.")
        sys.exit(0)
    if not choice.isdigit():
        if exists(pathlib.Path(choice)):
            studio_root = pathlib.Path(choice)
        else:
            print("That path does not exist. Exiting.")
            sys.exit(1)
    elif int(choice) < 1 or int(choice) > len(options):
        print("That was not an option. Exiting.")
        sys.exit(1)
    else:
        studio_root = options[int(choice) - 1][0]

    studio_data_root = studio_root / "data"
else:
    path = " ".join(sys.argv[1:])
    studio_data_root = pathlib.Path(path)
    if not exists(studio_data_root):
        print("The path you provided does not exist. Exiting.")
        sys.exit(1)

elevate(str(studio_data_root))
logfile = open(log_file, "w", errors="replace", encoding="utf-8")

ensure_backup_original()

load_rules()

table = get_part_definition()

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
        txt = f"{part_id:<8} {row[6]:<80} => {name:>40}"
        print(txt, file=logfile)
        print(txt)
    row[6] = name

store_part_definition(table)

logfile.close()
