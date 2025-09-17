import os
import json
import yaml
from pathlib import Path
from jinja2 import Template

def load_database_file(database_path):
    """Load the database JSON file containing model evaluation data."""
    try:
        with open(database_path, "r") as f:
            data = json.load(f)
        print(f"Loaded {len(data)} records from database")
        return data
    except FileNotFoundError:
        print(f"Database file not found at {database_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return []


def prepare_chart_data(data):
    """Prepare data for the chart visualization."""
    if not data:
        return [], []

    # Group data by model and eval_name for comparison
    model_scores = {}
    models = set()
    evals = set()

    print("Processing data entries...")
    entry_count = 0

    for item in data:
        model = item.get("model", "Unknown Model")
        eval_name = item.get("eval_name", "Unknown Eval")
        score = item.get("score", 0)

        # Skip error entries
        if score == "Error":
            print(f"Skipping error entry for model {model}, eval {eval_name}")
            continue

        entry_count += 1
        models.add(model)
        evals.add(eval_name)

        if model not in model_scores:
            model_scores[model] = {}

        if eval_name not in model_scores[model]:
            model_scores[model][eval_name] = []

        model_scores[model][eval_name].append(score)

    print(f"Processed {entry_count} valid entries")
    print(f"Found {len(models)} unique models and {len(evals)} unique evaluation tasks")

    # Show detailed breakdown
    for model in model_scores:
        for eval_name in model_scores[model]:
            scores = model_scores[model][eval_name]
            if len(scores) > 1:
                avg_score = sum(scores) / len(scores)
                print(
                    f"Model {model} on {eval_name}: {len(scores)} tests, scores={scores}, avg={avg_score:.4f}"
                )
            elif len(scores) == 1:
                print(f"Model {model} on {eval_name}: 1 test, score={scores[0]}")

    # Prepare chart data
    chart_labels = sorted(list(models))
    eval_names = sorted(list(evals))

    # For each eval, create a dataset
    datasets = []
    for eval_name in eval_names:
        scores = []
        for model in chart_labels:
            if model in model_scores and eval_name in model_scores[model]:
                model_scores_list = model_scores[model][eval_name]
                # Average multiple scores for the same model/eval combination
                avg_score = sum(model_scores_list) / len(model_scores_list)
                scores.append(round(avg_score, 4))
                if len(model_scores_list) > 1:
                    print(
                        f"Averaging {len(model_scores_list)} scores for {model} on {eval_name}: {avg_score:.4f}"
                    )
            else:
                scores.append(0)
        datasets.append({"label": eval_name, "data": scores, "borderWidth": 1})

    return chart_labels, datasets


def generate_chart_html(labels, datasets, outputs_path="reports"):
    """Generate an HTML file with interactive charts using Chart.js."""
    # Convert data to JSON for JavaScript
    labels_json = json.dumps(labels)
    datasets_json = json.dumps(datasets)

    template_path = Path(__file__).parent / "templates/chart_html.j2"
    html_template = Template(template_path.read_text(encoding="utf-8"))

    html_rendered = html_template.render(
        labels_json=labels_json,
        datasets_json=datasets_json,
    )

    output_path = Path(f"{outputs_path}/chart.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_rendered, encoding="utf-8")

    print(f"Chart HTML saved to {output_path}")


def build_charts(config_file_path):
    """Main function to generate the performance charts."""
    output_yaml = yaml.safe_load(Path(config_file_path).read_text())
    # logs_path = output_yaml["evaluation"]["output"]["logs"]
    reports_path = output_yaml["evaluation"]["output"]["reports"]

    # Load data from database
    data = load_database_file(reports_path + "/database.json")

    if not data:
        print("No data available to generate charts.")
        return

    # Prepare chart data
    labels, datasets = prepare_chart_data(data)

    if not labels or not datasets:
        print("No valid data to display in charts.")
        return

    # Generate the HTML chart
    generate_chart_html(labels, datasets)

    print("Chart generation completed successfully!")
