import json
import os
from datetime import datetime


def load_database_file(database_path="docs/database.json"):
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

    for item in data:
        model = item.get("model", "Unknown Model")
        eval_name = item.get("eval_name", "Unknown Eval")
        score = item.get("score", 0)
        
        # Skip error entries
        if score == "Error":
            continue
            
        models.add(model)
        evals.add(eval_name)
        
        if model not in model_scores:
            model_scores[model] = {}
            
        if eval_name not in model_scores[model]:
            model_scores[model][eval_name] = []
            
        model_scores[model][eval_name].append(score)

    # Prepare chart data
    chart_labels = sorted(list(models))
    eval_names = sorted(list(evals))
    
    # For each eval, create a dataset
    datasets = []
    for eval_name in eval_names:
        scores = []
        for model in chart_labels:
            if model in model_scores and eval_name in model_scores[model]:
                # Average multiple scores for the same model/eval combination
                avg_score = sum(model_scores[model][eval_name]) / len(model_scores[model][eval_name])
                scores.append(round(avg_score, 4))
            else:
                scores.append(0)
        datasets.append({
            "label": eval_name,
            "data": scores,
            "borderWidth": 1
        })

    return chart_labels, datasets


def generate_chart_html(labels, datasets, output_path="docs/chart.html"):
    """Generate an HTML file with interactive charts using Chart.js."""
    # Convert data to JSON for JavaScript
    labels_json = json.dumps(labels)
    datasets_json = json.dumps(datasets)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Model Performance Charts</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #333;
        }}
        .chart-container {{
            position: relative;
            height: 500px;
            margin-bottom: 40px;
        }}
        .description {{
            margin-bottom: 30px;
            line-height: 1.6;
            color: #666;
        }}
        .controls {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
        .control-group {{
            flex: 1;
            min-width: 200px;
        }}
        .control-group label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }}
        .control-group select {{
            width: 100%;
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }}
        .control-group button {{
            width: 100%;
            padding: 8px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 10px;
        }}
        .control-group button:hover {{
            background-color: #0056b3;
        }}
        @media (max-width: 768px) {{
            .controls {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Model Performance Comparison</h1>
        
        <div class="description">
            <p>This chart shows the performance scores of different models across various evaluation tasks. 
            Higher scores indicate better performance. Use the filters below to customize the view.</p>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label for="modelFilter">Filter by Model:</label>
                <select id="modelFilter" multiple size="4">
                    <option value="" selected>All Models</option>
                </select>
                <button id="applyModelFilter">Apply Model Filter</button>
            </div>
            
            <div class="control-group">
                <label for="evalFilter">Filter by Evaluation:</label>
                <select id="evalFilter" multiple size="4">
                    <option value="" selected>All Evaluations</option>
                </select>
                <button id="applyEvalFilter">Apply Evaluation Filter</button>
            </div>
            
            <div class="control-group">
                <label>&nbsp;</label>
                <button id="resetFilters">Reset All Filters</button>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="performanceChart"></canvas>
        </div>
    </div>

    <script>
        // Chart data (full dataset)
        const allLabels = {labels_json};
        const allDatasets = {datasets_json};
        
        // Current chart data (filtered)
        let currentLabels = [...allLabels];
        let currentDatasets = JSON.parse(JSON.stringify(allDatasets)); // Deep copy
        
        // Apply distinct colors to each dataset
        const backgroundColors = [
            'rgba(255, 99, 132, 0.2)',
            'rgba(54, 162, 235, 0.2)',
            'rgba(255, 206, 86, 0.2)',
            'rgba(75, 192, 192, 0.2)',
            'rgba(153, 102, 255, 0.2)',
            'rgba(255, 159, 64, 0.2)',
            'rgba(199, 199, 199, 0.2)'
        ];
        
        const borderColors = [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)',
            'rgba(199, 199, 199, 1)'
        ];
        
        // Add colors to datasets
        currentDatasets.forEach((dataset, index) => {{
            dataset.backgroundColor = backgroundColors[index % backgroundColors.length];
            dataset.borderColor = borderColors[index % borderColors.length];
        }});
        
        // Create the chart
        const ctx = document.getElementById('performanceChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: currentLabels,
                datasets: currentDatasets
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Score'
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Models'
                        }}
                    }}
                }},
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Model Performance by Evaluation Task'
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.dataset.label + ': ' + context.parsed.y.toFixed(4);
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Populate filter dropdowns
        function populateFilters() {{
            const modelFilter = document.getElementById('modelFilter');
            const evalFilter = document.getElementById('evalFilter');
            
            // Clear existing options except the first one
            modelFilter.innerHTML = '<option value="" selected>All Models</option>';
            evalFilter.innerHTML = '<option value="" selected>All Evaluations</option>';
            
            // Add model options
            allLabels.forEach(model => {{
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelFilter.appendChild(option);
            }});
            
            // Add evaluation options
            allDatasets.forEach(dataset => {{
                const option = document.createElement('option');
                option.value = dataset.label;
                option.textContent = dataset.label;
                evalFilter.appendChild(option);
            }});
        }}
        
        // Apply model filter
        function applyModelFilter() {{
            const selectedModels = Array.from(document.getElementById('modelFilter').selectedOptions)
                .map(option => option.value)
                .filter(value => value !== "");
                
            if (selectedModels.length === 0) {{
                currentLabels = [...allLabels];
            }} else {{
                currentLabels = allLabels.filter(label => selectedModels.includes(label));
            }}
            
            updateChart();
        }}
        
        // Apply evaluation filter
        function applyEvalFilter() {{
            const selectedEvals = Array.from(document.getElementById('evalFilter').selectedOptions)
                .map(option => option.value)
                .filter(value => value !== "");
                
            if (selectedEvals.length === 0) {{
                currentDatasets = JSON.parse(JSON.stringify(allDatasets));
            }} else {{
                currentDatasets = allDatasets.filter(dataset => selectedEvals.includes(dataset.label));
            }}
            
            // Reapply colors
            currentDatasets.forEach((dataset, index) => {{
                dataset.backgroundColor = backgroundColors[index % backgroundColors.length];
                dataset.borderColor = borderColors[index % borderColors.length];
            }});
            
            updateChart();
        }}
        
        // Reset all filters
        function resetFilters() {{
            const modelFilter = document.getElementById('modelFilter');
            const evalFilter = document.getElementById('evalFilter');
            
            // Clear selections
            Array.from(modelFilter.options).forEach(option => option.selected = false);
            Array.from(evalFilter.options).forEach(option => option.selected = false);
            modelFilter.options[0].selected = true;
            evalFilter.options[0].selected = true;
            
            // Reset to full dataset
            currentLabels = [...allLabels];
            currentDatasets = JSON.parse(JSON.stringify(allDatasets));
            
            // Reapply colors
            currentDatasets.forEach((dataset, index) => {{
                dataset.backgroundColor = backgroundColors[index % backgroundColors.length];
                dataset.borderColor = borderColors[index % borderColors.length];
            }});
            
            updateChart();
        }}
        
        // Update chart with current data
        function updateChart() {{
            chart.data.labels = currentLabels;
            chart.data.datasets = currentDatasets;
            chart.update();
        }}
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            populateFilters();
            
            // Add event listeners
            document.getElementById('applyModelFilter').addEventListener('click', applyModelFilter);
            document.getElementById('applyEvalFilter').addEventListener('click', applyEvalFilter);
            document.getElementById('resetFilters').addEventListener('click', resetFilters);
        }});
    </script>
</body>
</html>"""

    # Write the HTML file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html_content)
    
    print(f"Chart HTML saved to {output_path}")


def main():
    """Main function to generate the performance charts."""
    # Load data from database
    data = load_database_file()
    
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


if __name__ == "__main__":
    main()