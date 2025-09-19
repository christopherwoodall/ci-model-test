import json
from jinja2 import Template
from pathlib import Path


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


def prepare_spider_chart_data(data):
    """Prepare data for a spider (radar) chart visualization."""
    if not data:
        return [], []

    model_scores = {}
    eval_names = set()

    print("Processing data entries for spider chart...")
    for item in data:
        model = item.get("model")
        eval_name = item.get("eval_name")
        score = item.get("score")

        if score == "Error" or model is None or eval_name is None:
            continue

        if model not in model_scores:
            model_scores[model] = {}

        if eval_name not in model_scores[model]:
            model_scores[model][eval_name] = []

        model_scores[model][eval_name].append(score)
        eval_names.add(eval_name)

    # Normalize scores to a 0-1 range to make them comparable on the chart
    # First, find the min and max scores for each evaluation
    eval_min_max = {eval: {"min": 1, "max": 0} for eval in eval_names}
    for model in model_scores:
        for eval_name, scores in model_scores[model].items():
            if scores:
                avg_score = sum(scores) / len(scores)
                eval_min_max[eval_name]["min"] = min(
                    eval_min_max[eval_name]["min"], avg_score
                )
                eval_min_max[eval_name]["max"] = max(
                    eval_min_max[eval_name]["max"], avg_score
                )

    # Create datasets for the spider chart
    datasets = []
    for model, evals in model_scores.items():
        scores = []
        for eval_name in sorted(list(eval_names)):
            if eval_name in evals:
                avg_score = sum(evals[eval_name]) / len(evals[eval_name])
                # Normalize the score
                min_val = eval_min_max[eval_name]["min"]
                max_val = eval_min_max[eval_name]["max"]
                if max_val > min_val:
                    normalized_score = (avg_score - min_val) / (max_val - min_val)
                else:
                    normalized_score = 0
                scores.append(round(normalized_score, 4))
            else:
                scores.append(0)
        datasets.append({"label": model, "data": scores, "borderWidth": 1})

    return sorted(list(eval_names)), datasets


def generate_spider_chart_html(labels, datasets, outputs_path="reports"):
    """Generate an HTML file with an interactive spider chart using Chart.js."""
    labels_json = json.dumps(labels)
    datasets_json = json.dumps(datasets)

    template_path = Path(__file__).parent / "templates/spider_chart.j2"
    # Ensure the template exists
    if not template_path.exists():
        print(f"Error: Template file not found at {template_path}")
        return

    html_template = Template(template_path.read_text(encoding="utf-8"))
    html_rendered = html_template.render(
        labels_json=labels_json,
        datasets_json=datasets_json,
    )

    output_path = Path(f"{outputs_path}/spider_chart.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_rendered, encoding="utf-8")

    print(f"Spider chart HTML saved to {output_path}")


def build_spider_chart(config):
    """Main function to generate the spider chart."""
    reports_path = config["evaluation"]["output"]["reports"]

    data = load_database_file(str(Path(reports_path) / "database.json"))

    if not data:
        print("No data available to generate charts.")
        return

    labels, datasets = prepare_spider_chart_data(data)

    if not labels or not datasets:
        print("No valid data to display in the spider chart.")
        return

    generate_spider_chart_html(labels, datasets, reports_path)

    print("Spider chart generation completed successfully!")
