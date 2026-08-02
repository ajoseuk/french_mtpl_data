#!/usr/bin/env python3
"""Download OpenML's French MTPL frequency data and retain it as CSV."""

from __future__ import annotations

import argparse
import csv
import io
import os
import tempfile
import urllib.request
from pathlib import Path


DATA_URL = "https://www.openml.org/data/v1/download/20649148/freMTPL2freq.arff"
DEFAULT_OUTPUT = Path(__file__).with_name("freMTPL2freq.csv")


def convert_arff(source: io.TextIOBase, destination: io.TextIOBase) -> int:
    """Convert the simple, dense OpenML ARFF stream to CSV."""
    columns: list[str] = []
    in_data = False
    writer = csv.writer(destination, lineterminator="\n")
    rows = 0

    for raw_line in source:
        line = raw_line.strip()
        if not line or line.startswith("%"):
            continue
        if not in_data:
            lowered = line.lower()
            if lowered.startswith("@attribute"):
                remainder = line[len("@attribute") :].lstrip()
                if remainder[0] in "'\"":
                    quote = remainder[0]
                    end = remainder.find(quote, 1)
                    columns.append(remainder[1:end])
                else:
                    columns.append(remainder.split(None, 1)[0])
            elif lowered == "@data":
                if not columns:
                    raise ValueError("ARFF input has no attributes")
                writer.writerow(columns)
                in_data = True
            continue

        values = next(csv.reader([line], skipinitialspace=True))
        if len(values) != len(columns):
            raise ValueError(f"row has {len(values)} values; expected {len(columns)}")
        writer.writerow(values)
        rows += 1

    if not in_data:
        raise ValueError("ARFF input has no @data section")
    return rows


def download(output: Path, force: bool = False) -> int:
    if output.exists() and not force:
        print(f"Retaining existing file: {output}")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(DATA_URL, headers={"User-Agent": "fremtpl-csv-downloader/1.0"})
    temporary_name: str | None = None
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            encoding = response.headers.get_content_charset() or "utf-8"
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", newline="", dir=output.parent, delete=False
            ) as temporary:
                temporary_name = temporary.name
                rows = convert_arff(io.TextIOWrapper(response, encoding=encoding), temporary)
        os.replace(temporary_name, output)
    except BaseException:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)
        raise

    print(f"Wrote {rows:,} rows to {output}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true", help="replace an existing CSV")
    args = parser.parse_args()
    download(args.output, args.force)


if __name__ == "__main__":
    main()
