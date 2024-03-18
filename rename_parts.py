import os
import re
import pathlib
import ctypes
from elevate import elevate as _elevate
import glob


config_root = pathlib.Path(__file__).parent.absolute()
studio_data_root = pathlib.Path(r"C:\Program Files\Studio 2.0\data")

regex_rules = {}
id_rules = {}


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def elevate():
    if not is_admin():
        print("Not admin, elevating...")
        print("If you are on windows, you won't see the log output in the console, but it will be in log.txt.")
        _elevate()


def _load_id_rules(file_path):
    with open(file_path, "r", errors="replace", encoding="utf-8") as f:
        mapping_raw = f.read()
        mapping = {
            x[0]: x[1]
            for x in (
                y.split(" => ") for y in mapping_raw.split("\n") if y.strip() != ""
            )
        }
    id_rules.update(mapping)


def _load_regex_rules(file_path):
    with open(file_path, "r", errors="replace", encoding="utf-8") as f:
        mapping_raw = f.read()
        mapping = {
            re.compile(x[0]): x[1]
            for x in (
                y.split(" => ") for y in mapping_raw.split("\n") if y.strip() != ""
            )
        }
    regex_rules.update(mapping)


def load_rules():
    for file in glob.glob(str(config_root / "rules" / "*.id.rules")):
        _load_id_rules(file)
    for file in glob.glob(str(config_root / "rules" / "*.regex.rules")):
        _load_regex_rules(file)


def ensure_backup_original():
    if not os.path.exists(
        str(studio_data_root / "StudioPartDefinition2.txt.original")
    ):
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
    table = [re.split(r"\t", line) for line in lines]

    return table


def store_part_definition(table):
    new_content = "Studio " + "\n".join(["\t".join(row) for row in table])
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

elevate()

logfile = open("log.txt", "w", errors="replace", encoding="utf-8")

ensure_backup_original()

load_rules()

table = get_part_definition()

for row in table:
    if len(row) < 7:
        continue
    name = row[6]
    id = row[2]
    if id in id_rules:
        name = id_rules[id]
    for k, v in regex_rules.items():
        name = re.sub(k, generate_regex_result(v), name)
    if name != row[6]:
        txt = f"{id:<8} {row[6]:<80} => {name:>40}"
        print(txt, file=logfile)
        print(txt)
    row[6] = name

store_part_definition(table)

logfile.close()
