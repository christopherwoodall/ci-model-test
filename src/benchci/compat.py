import json
from pathlib import Path


def iter_json_files(logs_path):
    """Yield JSON objects from all JSON files in the logs directory."""
    # TODO - Better define output paths (config.yaml?) - evaluation.py:28
    logs_dir = Path(logs_path)

    for file_path in logs_dir.glob("*.json"):
        yield file_path


def compat_logs(config):
    logs_path = config["evaluation"]["output"]["logs"]

    for record in iter_json_files(logs_path=logs_path):
        # If the file is already compat, skip it
        if "_compat" in record.name:
            continue

        try:
            with record.open("r", encoding="utf-8") as f:
                record_json = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {record}")
            continue

        # Remove evaluation content from the JSON
        record_json.pop("samples", None)
        record_json.pop("reductions", None)

        # Write the modified JSON back to the file
        with record.open("w", encoding="utf-8") as f:
            json.dump(record_json, f, indent=4, sort_keys=True, ensure_ascii=False)

        # Strip all "_compats" first to avoid multiple suffixes
        compat_stem = record.stem.replace("_compat", "")
        # Rename the file to prepend "_compat"
        compat_rename = record.with_name(f"{compat_stem}_compat{record.suffix}")
        record.rename(compat_rename)

        print(f"Processed {record} and saved compacted version as {compat_rename}")

    print("Log compaction complete.")
