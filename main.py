"""
Studio Custom Names is a program to change the names of the parts in Studio 2.0.
Copyright (C) 2024 GSG-Robots & J0J0HA

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


config_root = pathlib.Path(__file__).parent.absolute()

regex_rules = {}
id_rules = {}


print("""
Studio Custom Names - Copyright (C) 2024  GSG-Robots & J0J0HA
This program comes with ABSOLUTELY NO WARRANTY; for details see the LICENSE-file.
This is free software, and you are welcome to redistribute it
under certain conditions; for details see the LICENSE-file.
""")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return os.getuid() == 0


def elevate():
    if not is_admin():
        print("Not admin, elevating...")
        print(
            "If you are on windows, you won't see the log output in the console, but it will be in log.txt."
        )
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)

def is_studio_installed():
    return os.path.exists(str(studio_root))

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

studio_root = pathlib.Path(r"C:\Program Files\Studio 2.0")

if not is_studio_installed():
    studio_root = pathlib.Path(r"C:\Program Files (x86)\Studio 2.0 EarlyAccess")
    
if not is_studio_installed():
    print("Studio was not found on the default install location.")
    new_path = input("Please enter the path to the Studio installation: ")
    studio_root = pathlib.Path(new_path)
    if not is_studio_installed():
        print("Studio was not found on the specified path.")
        sys.exit(1)
else:
    print("Studio was not found on the default install location, but Studio EarlyAccess was.")

print(f"Using Studio installation at: {studio_root}")

studio_data_root = studio_root / "data"

elevate()

logfile = open("log.txt", "w", errors="replace", encoding="utf-8")

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
