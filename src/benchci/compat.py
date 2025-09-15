"""
Issue: Logs can be large and hard to check-in without using git-lfs.

Solution: Once it is determined that the logs need to be compacted,
          this script can be ran to remove evaluation content (e.g.
          chat completions/responses) so that only the metrics
          remain. This is a destructive operation - the content of
          the evaluations will be lost.

Process:
    1. log directory is scanned.
    2. filter out any files that do not end with `_compat`.
    3. Read, modify, and write back the file contents. (remove all eval data leaving only metrics)
    4. rename the file prepending `_compat`.

Considerations:
    * Better handling on the output directory. It is currently defined seperately in evaluation.py:28 and
      pages.py:8. It would be nice if it was defined globally at initialization.
    * This brings up the larger issue of how should the original runs be stored? Serialized in a database?
      Added to an application directory? Tokens are cheap, delete and rerun?
    * All generated assets (html, css, js) should be templated.
"""

import json
from pathlib import Path


def iter_json_files(logs_path="./logs/"):
    """Yield JSON objects from all JSON files in the logs directory."""
    # TODO - Better define output paths (config.yaml?) - evaluation.py:28
    logs_dir = Path(logs_path)

    for file_path in logs_dir.glob("*.json"):
        yield file_path


def compat_logs():
    # TODO - Better define output paths (config.yaml?) - evaluation.py:28
    for record in iter_json_files("./logs/"):
        try:
            with record.open("r", encoding="utf-8") as f:
                record_json = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {record}")
            continue

        # If the file is already compat, skip it
        if "_compat" in record.name:
            continue
        
        # TODO - Check if error exists in log and remove it?

        # Remove evaluation content from the JSON
        record_json.pop("samples", None)
        record_json.pop("reductions", None)

        # Write the modified JSON back to the file
        with record.open("w", encoding="utf-8") as f:
            json.dump(record_json, f, indent=4, sort_keys=True, ensure_ascii=False)

        # Rename the file to prepend "_compat"
        compat_rename = record.with_name(f"{record.stem}_compat{record.suffix}")
        record.rename(compat_rename)

        print(f"Processed {record} and saved compacted version as {compat_rename}")
