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

from pathlib import Path
import json



def iter_json_files(logs_path="./logs/"):
    """Yield JSON objects from all JSON files in the logs directory."""
    # TODO - Better define output paths (config.yaml?) - evaluation.py:28
    logs_dir = Path(logs_path)

    for file_path in logs_dir.glob("*.json"):
        try:
            with file_path.open("r", encoding="utf-8") as f:
                yield json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {file_path}")
            continue


def compat_logs():
    # TODO - Better define output paths (config.yaml?) - evaluation.py:28
    for record in iter_json_files("./logs/"):
        # if "_compat" in record.filename: pass

        # record_json = json.loads(record.read())
        # extraction/removal logic
        # write back the file
        # rename the file

        print(record)
