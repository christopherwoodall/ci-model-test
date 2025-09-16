# ruff: noqa: B007 E501
import json
import yaml
from jinja2 import Template
from pathlib import Path
from datetime import datetime


def load_json_files(logs_path):
    """Load all JSON files from the logs directory."""
    logs_dir = Path(logs_path)
    report_data = []

    for file_path in logs_dir.glob("*.json"):
        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                report_data.append(data)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {file_path}")
            continue

    return report_data


def convert_to_database_format(report_data):
    """Convert the report data to a database-friendly format."""
    database_entries = []

    # TODO - This needs to be reworked. Use iter (see compat.py) so that
    #        we're not loading every file into memory.
    for item in report_data:
        model = item.get("eval", {}).get("model", "N/A")
        timestamp = item.get("eval", {}).get("created", "N/A")
        eval_name = item.get("eval", {}).get("task", "N/A")

        # Parse timestamp if it's not 'N/A'
        if timestamp != "N/A":
            try:
                # Handle different timestamp formats
                if isinstance(timestamp, str):
                    parsed_timestamp = datetime.fromisoformat(
                        timestamp.replace("Z", "+00:00")
                    )
                else:
                    parsed_timestamp = datetime.fromtimestamp(timestamp)
                formatted_timestamp = parsed_timestamp.isoformat()
            except Exception:
                formatted_timestamp = timestamp
        else:
            formatted_timestamp = "N/A"

        # Extract score and additional metrics
        score_val = "Error"
        additional_metrics = {}
        if item.get("status") != "error":
            try:
                # Primary accuracy score
                score_val = item["results"]["scores"][0]["metrics"]["accuracy"]["value"]

                # Additional metrics
                metrics = item["results"]["scores"][0]["metrics"]
                for metric_name, metric_data in metrics.items():
                    if metric_name != "accuracy":  # Skip the main accuracy metric
                        additional_metrics[metric_name] = metric_data["value"]
            except (KeyError, IndexError):
                pass

        # Model usage data
        model_usage = item.get("stats", {}).get("model_usage", {})
        total_input_tokens = 0
        total_output_tokens = 0
        total_tokens = 0

        for model_key, usage_data in model_usage.items():
            total_input_tokens += usage_data.get("input_tokens", 0)
            total_output_tokens += usage_data.get("output_tokens", 0)
            total_tokens += usage_data.get("total_tokens", 0)

        database_entries.append(
            {
                "model": model,
                "model_key": model_key,
                "timestamp": formatted_timestamp,
                "eval_name": eval_name,
                "score": (
                    score_val if isinstance(score_val, (int, float)) else score_val
                ),
                "additional_metrics": additional_metrics,
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "total_tokens": total_tokens,
            }
        )

    return database_entries


def save_to_json_file(data, reports_path):
    """Save the database entries to a JSON file."""
    with open(f"{reports_path}/database.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Database saved to {reports_path}")


def generate_html_page(reports_path):
    """Generate an HTML page to display the data using Jinja2."""
    template_path = Path(__file__).parent / "templates/report_html.j2"
    html_template = Template(template_path.read_text(encoding="utf-8"))

    html_rendered = html_template.render(
        title="Model Evaluation Report",
        css_file="report.css",
        data_file="database.json",
    )

    output_path = Path(f"{reports_path}/index.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_rendered, encoding="utf-8")

    print(f"HTML page saved to {output_path}")


def generate_css():
    """Generate CSS for the HTML page."""
    # TODO - use jinja
    css_code = """/* Report Page Styles */

.report-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: #fff;
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
  font-family: Arial, sans-serif;
}

.report-container h1 {
  text-align: center;
  color: #444;
  margin-bottom: 20px;
}

.filters {
  margin-bottom: 20px;
}

.search-container {
  margin-bottom: 15px;
}

.search-container input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  box-sizing: border-box;
}

.filter-dropdowns {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-dropdowns select,
.filter-dropdowns button {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.filter-dropdowns button {
  background: #007bff;
  color: white;
  border: 1px solid #007bff;
  cursor: pointer;
}

.filter-dropdowns button:hover {
  background: #0056b3;
}

.results-info {
  margin-bottom: 15px;
  font-weight: bold;
  color: #666;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.report-table th,
.report-table td {
  padding: 12px;
  border: 1px solid #ddd;
  text-align: left;
}

.report-table th {
  background-color: #f2f2f2;
  cursor: pointer;
  user-select: none;
}

.report-table th:hover {
  background-color: #e0e0e0;
}

.report-table tr:nth-child(even) {
  background-color: #f9f9f9;
}

.report-table tr:hover {
  background-color: #f1f1f1;
}

.report-table button {
  padding: 6px 12px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.report-table button:hover {
  background: #218838;
}

/* Modal Styles */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 800px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
}

.close {
  position: absolute;
  top: 10px;
  right: 15px;
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.metric-card {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 15px;
}

.metric-card h3 {
  margin-top: 0;
  color: #495057;
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 8px;
}

.metric-card p {
  margin: 8px 0;
}

/* Responsive design */
@media (max-width: 768px) {
  .filter-dropdowns {
    flex-direction: column;
  }
  
  .filter-dropdowns select,
  .filter-dropdowns button {
    width: 100%;
  }
  
  .report-table {
    font-size: 14px;
  }
  
  .report-table th,
  .report-table td {
    padding: 8px;
  }
}"""

    with open("reports/report.css", "w") as f:
        f.write(css_code)
    print("CSS file saved to reports/report.css")


def build_pages(config_file_path):
    """Main function to orchestrate the build process."""
    output_yaml = yaml.safe_load(Path(config_file_path).read_text())
    logs_path = output_yaml["evaluation"]["output"]["logs"]
    reports_path = output_yaml["evaluation"]["output"]["reports"]

    # Load JSON files
    report_data = load_json_files(logs_path)

    if not report_data:
        print("No data found to generate a report.")
        return

    # Convert to database format
    database_entries = convert_to_database_format(report_data)

    # Save to JSON file (this will be our "database")
    save_to_json_file(database_entries, reports_path)

    # Generate HTML page
    generate_html_page(reports_path)

    # Generate CSS
    generate_css()

    print("Build process completed successfully!")
