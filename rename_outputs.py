
from pathlib import Path
import re

output_dir = Path("output")

def normalize_filename(name):
    name = name.strip().lower()
    name = name.replace("&", "_and_")
    name = name.replace("%", "pct")
    name = re.sub(r"[\s\-]+", "_", name)
    name = re.sub(r"_+", "_", name)
    return name

for file in sorted(output_dir.iterdir()):
    if not file.is_file():
        continue

    if file.suffix.lower() == ".png":
        continue

    new_name = normalize_filename(file.stem)

    # Correct known spelling issue
    new_name = new_name.replace("upflift", "uplift")

    # Preview only; do not rename yet
    proposed = f"{new_name}.csv"

    print(f"{file.name}  -->  {proposed}")


import csv

print("\n--- CSV Format Check ---")

for file in sorted(output_dir.iterdir()):
    if not file.is_file() or file.suffix.lower() == ".png":
        continue

    try:
        with file.open(
            "r", encoding="utf-8-sig", newline=""
        ) as f:
            sample = f.read(4096)

        dialect = csv.Sniffer().sniff(
            sample, delimiters=",;\t"
        )

        print(
            f"{file.name}: "
            f"detected delimiter = {repr(dialect.delimiter)}"
        )

    except (csv.Error, UnicodeError) as e:
        print(f"{file.name}: CHECK MANUALLY ({e})")
