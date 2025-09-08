# ruff: noqa: B007 E501
import os
import glob
import json
from datetime import datetime


def load_json_files(logs_path="logs"):
    """Load all JSON files from the logs directory."""
    json_files = glob.glob(os.path.join(logs_path, "*.json"))
    report_data = []

    for file_path in json_files:
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                report_data.append(data)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {file_path}")
                continue

    return report_data


def convert_to_database_format(report_data):
    """Convert the report data to a database-friendly format."""
    database_entries = []

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


def save_to_json_file(data, output_path="docs/database.json"):
    """Save the database entries to a JSON file."""
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Database saved to {output_path}")


def generate_html_page():
    """Generate an HTML page to display the data."""
    html_code = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Model Evaluation Report</title>
    <link rel="stylesheet" href="ReportPage.css">
</head>
<body>
    <div class="report-container">
        <h1>Model Evaluation Report</h1>
        
        <div class="filters">
            <div class="search-container">
                <input type="text" id="searchInput" placeholder="Search models or evals...">
            </div>
            
            <div class="filter-dropdowns">
                <select id="modelFilter">
                    <option value="">All Models</option>
                </select>
                
                <select id="evalFilter">
                    <option value="">All Evals</option>
                </select>
                
                <button id="clearFilters">Clear Filters</button>
            </div>
        </div>
        
        <div class="results-info">
            Showing <span id="resultCount">0</span> results
        </div>
        
        <table class="report-table">
            <thead>
                <tr>
                    <th data-sort="model">Model</th>
                    <th data-sort="timestamp">Timestamp</th>
                    <th data-sort="eval_name">Eval Name</th>
                    <th data-sort="score">Score</th>
                    <th data-sort="total_tokens">Total Tokens</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody id="reportTableBody">
                <!-- Data will be populated by JavaScript -->
            </tbody>
        </table>
    </div>
    
    <script>
        // Load data from database.json
        fetch('database.json')
            .then(response => response.json())
            .then(data => {
                // Populate filter dropdowns
                const uniqueModels = [...new Set(data.map(item => item.model))];
                const uniqueEvals = [...new Set(data.map(item => item.eval_name))];
                
                const modelFilter = document.getElementById('modelFilter');
                const evalFilter = document.getElementById('evalFilter');
                
                uniqueModels.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = model;
                    modelFilter.appendChild(option);
                });
                
                uniqueEvals.forEach(evalName => {
                    const option = document.createElement('option');
                    option.value = evalName;
                    option.textContent = evalName;
                    evalFilter.appendChild(option);
                });
                
                // Store original data
                window.originalData = data;
                window.filteredData = [...data];
                
                // Render initial table
                renderTable(data);
                
                // Set up event listeners
                setupEventListeners();
            })
            .catch(error => console.error('Error loading data:', error));
            
        function setupEventListeners() {
            // Search functionality
            document.getElementById('searchInput').addEventListener('input', function(e) {
                applyFilters();
            });
            
            // Model filter
            document.getElementById('modelFilter').addEventListener('change', function(e) {
                applyFilters();
            });
            
            // Eval filter
            document.getElementById('evalFilter').addEventListener('change', function(e) {
                applyFilters();
            });
            
            // Clear filters
            document.getElementById('clearFilters').addEventListener('click', function() {
                document.getElementById('searchInput').value = '';
                document.getElementById('modelFilter').value = '';
                document.getElementById('evalFilter').value = '';
                window.filteredData = [...window.originalData];
                renderTable(window.filteredData);
            });
            
            // Sort functionality
            document.querySelectorAll('th[data-sort]').forEach(th => {
                th.addEventListener('click', function() {
                    const sortKey = this.getAttribute('data-sort');
                    sortTable(sortKey);
                });
            });
        }
        
        function applyFilters() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const selectedModel = document.getElementById('modelFilter').value;
            const selectedEval = document.getElementById('evalFilter').value;
            
            let result = window.originalData;
            
            // Apply search filter
            if (searchTerm) {
                result = result.filter(item => {
                    return (
                        item.model.toLowerCase().includes(searchTerm) ||
                        item.eval_name.toLowerCase().includes(searchTerm)
                    );
                });
            }
            
            // Apply model filter
            if (selectedModel) {
                result = result.filter(item => item.model === selectedModel);
            }
            
            // Apply eval filter
            if (selectedEval) {
                result = result.filter(item => item.eval_name === selectedEval);
            }
            
            window.filteredData = result;
            renderTable(result);
        }
        
        function sortTable(sortKey) {
            const sortedData = [...window.filteredData].sort((a, b) => {
                let aValue = a[sortKey];
                let bValue = b[sortKey];
                
                // Special handling for timestamp column
                if (sortKey === 'timestamp') {
                    aValue = new Date(aValue).getTime();
                    bValue = new Date(bValue).getTime();
                } else {
                    // Try numeric comparison for score
                    const aNum = parseFloat(aValue);
                    const bNum = parseFloat(bValue);
                    if (!isNaN(aNum) && !isNaN(bNum)) {
                        aValue = aNum;
                        bValue = bNum;
                    }
                }
                
                if (aValue < bValue) {
                    return -1;
                }
                if (aValue > bValue) {
                    return 1;
                }
                return 0;
            });
            
            window.filteredData = sortedData;
            renderTable(sortedData);
        }
        
        function renderTable(data) {
            const tableBody = document.getElementById('reportTableBody');
            tableBody.innerHTML = '';
            
            document.getElementById('resultCount').textContent = data.length;
            
            data.forEach((item, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${item.model}</td>
                    <td>${new Date(item.timestamp).toLocaleString()}</td>
                    <td>${item.eval_name}</td>
                    <td>${typeof item.score === 'number' ? item.score.toFixed(4) : item.score}</td>
                    <td>${item.total_tokens?.toLocaleString() || 'N/A'}</td>
                    <td><button class="details-btn" data-index="${index}">Show Details</button></td>
                `;
                tableBody.appendChild(row);
            });
            
            // Add event listeners to detail buttons
            document.querySelectorAll('.details-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const index = this.getAttribute('data-index');
                    showDetails(index);
                });
            });
        }
        
        function showDetails(index) {
            const item = window.filteredData[index];
            const details = `
                <div class="modal">
                    <div class="modal-content">
                        <span class="close">&times;</span>
                        <h2>Details for ${item.model} - ${item.eval_name}</h2>
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <h3>Token Usage</h3>
                                <p><strong>Input:</strong> ${item.total_input_tokens?.toLocaleString() || 'N/A'}</p>
                                <p><strong>Output:</strong> ${item.total_output_tokens?.toLocaleString() || 'N/A'}</p>
                                <p><strong>Total:</strong> ${item.total_tokens?.toLocaleString() || 'N/A'}</p>
                            </div>
                            
                            <div class="metric-card">
                                <h3>Primary Metrics</h3>
                                <p><strong>Score:</strong> ${typeof item.score === 'number' ? item.score.toFixed(4) : item.score}</p>
                                ${item.additional_metrics?.stderr !== undefined ? 
                                    `<p><strong>Std Error:</strong> ${item.additional_metrics.stderr.toFixed(6)}</p>` : ''}
                            </div>
                            
                            ${Object.keys(item.additional_metrics || {}).length > 0 ? `
                                <div class="metric-card">
                                    <h3>Additional Metrics</h3>
                                    ${Object.entries(item.additional_metrics).map(([key, value]) => 
                                        `<p><strong>${key}:</strong> ${typeof value === 'number' ? value.toFixed(6) : value}</p>`
                                    ).join('')}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
            
            // Add modal to body
            const modal = document.createElement('div');
            modal.innerHTML = details;
            document.body.appendChild(modal);
            
            // Add close functionality
            modal.querySelector('.close').addEventListener('click', function() {
                document.body.removeChild(modal);
            });
            
            // Close when clicking outside
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    document.body.removeChild(modal);
                }
            });
        }
    </script>
</body>
</html>"""

    with open("docs/index.html", "w") as f:
        f.write(html_code)
    print("HTML page saved to docs/index.html")


def generate_css():
    """Generate CSS for the HTML page."""
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

    with open("docs/ReportPage.css", "w") as f:
        f.write(css_code)
    print("CSS file saved to docs/ReportPage.css")


def build_pages():
    """Main function to orchestrate the build process."""
    # Load JSON files
    report_data = load_json_files()

    if not report_data:
        print("No data found to generate a report.")
        return

    # Convert to database format
    database_entries = convert_to_database_format(report_data)

    # Save to JSON file (this will be our "database")
    save_to_json_file(database_entries)

    # Generate HTML page
    generate_html_page()

    # Generate CSS
    generate_css()

    print("Build process completed successfully!")
