from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Dict, Iterable, List


def normalize_key(value: str) -> str:
    value = str(value or "").strip().lower()
    value = value.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    value = re.sub(r"[^a-z0-9]+", "", value)
    return value


def field_name_map(fields: Iterable[dict]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for field in fields:
        name = field.get("name", "")
        if not name:
            continue
        result[normalize_key(name)] = name

        # Helpful variants for common VADAFOK field naming.
        result[normalize_key(name.replace("_", " "))] = name
        result[normalize_key(name.replace("-", " "))] = name
    return result


def read_csv(path: Path) -> List[Dict[str, str]]:
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin-1"]
    last_error = None

    for enc in encodings:
        try:
            with path.open("r", encoding=enc, newline="") as f:
                sample = f.read(4096)
                f.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=",;	")
                except Exception:
                    dialect = csv.excel
                reader = csv.DictReader(f, dialect=dialect)
                return [{str(k or "").strip(): str(v or "").strip() for k, v in row.items()} for row in reader]
        except Exception as e:
            last_error = e

    raise last_error or RuntimeError("CSV konnte nicht gelesen werden.")


def read_xlsx(path: Path) -> List[Dict[str, str]]:
    from openpyxl import load_workbook

    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []

    headers = [str(v or "").strip() for v in rows[0]]
    result = []

    for row in rows[1:]:
        item = {}
        for idx, header in enumerate(headers):
            if not header:
                continue
            value = row[idx] if idx < len(row) else ""
            item[header] = "" if value is None else str(value).strip()
        if any(v for v in item.values()):
            result.append(item)

    return result


def read_table(path: Path) -> List[Dict[str, str]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return read_csv(path)
    if suffix == ".xlsx":
        return read_xlsx(path)
    raise ValueError(f"Nicht unterstütztes Format: {suffix}")


def rows_to_batch_items(rows: List[Dict[str, str]], template_name: str, fields: List[dict], output_prefix: str, profile: str) -> List[dict]:
    fmap = field_name_map(fields)
    items = []

    for idx, row in enumerate(rows, start=1):
        values: Dict[str, str] = {}

        for column, value in row.items():
            normalized = normalize_key(column)
            if normalized in fmap:
                values[fmap[normalized]] = value

        # Output name can be supplied by several common column names.
        output_name = (
            row.get("output_name")
            or row.get("Output Name")
            or row.get("filename")
            or row.get("Filename")
            or row.get("file")
            or row.get("File")
            or f"{output_prefix}_{idx:03d}"
        )

        items.append({
            "template": template_name,
            "output_name": output_name,
            "profile": profile,
            "values": values,
        })

    return items
