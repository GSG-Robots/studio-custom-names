import os
import re


with open(r"C:\Users\Anwender\Documents\GitHub\internalWorkspace\tools\part_rename.weiredformat", "r", errors="replace", encoding="utf-8") as f:
    mapping_raw = f.read()
    
    mapping = {re.compile(x[0]): x[1] for x in (y.split(" => ") for y in mapping_raw.split("\n") if y.strip() != "")}
    
with open(r"C:\Users\Anwender\Documents\GitHub\internalWorkspace\tools\id_rename.weiredformat", "r", errors="replace", encoding="utf-8") as f:
    id_mapping_raw = f.read()
    
    id_mapping = {x[0]: x[1] for x in (y.split(" => ") for y in id_mapping_raw.split("\n") if y.strip() != "")}

with open(r"C:\Program Files\Studio 2.0\data\StudioPartDefinition2.txt", "r", errors="replace", encoding="utf-8") as f:
    file_content = f.read()

if not os.path.exists(r"C:\Program Files\Studio 2.0\data\StudioPartDefinition2.txt.original"):
    with open(r"C:\Program Files\Studio 2.0\data\StudioPartDefinition2.txt.original", "w", errors="replace", encoding="utf-8") as f:
        f.write(file_content)

with open(r"C:\Program Files\Studio 2.0\data\StudioPartDefinition2.txt.original", "r", errors="replace", encoding="utf-8") as f:
    file_content = f.read()

if not file_content.startswith("Studio "):
    raise ValueError
else:
    file_content = file_content[len("Studio "):]

lines = file_content.split("\n")

table = [re.split(r"\t", line) for line in lines]


def resolve(s):
   return lambda m: s.format(*m.groups())

for row in table:
    if len(row) < 7:
        continue
    name = row[6]
    id = row[2]
    if id in id_mapping:
        name = id_mapping[id]
    for k, v in mapping.items():
        name = re.sub(k, resolve(v), name)
    if name != row[6]:
        print(f"Renamed:   {row[6]:<70} to:   {name}")
    row[6] = name

new_content = "\n".join(["\t".join(row) for row in table])

with open(r"C:\Program Files\Studio 2.0\data\StudioPartDefinition2.txt", "w", errors="replace", encoding="utf-8") as f:
    f.write(new_content)
