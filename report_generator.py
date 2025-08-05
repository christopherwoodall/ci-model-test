import os
import json
import glob
from datetime import datetime

def generate_html_report():
    logs_path = 'logs'
    json_files = glob.glob(os.path.join(logs_path, '*.json'))
    
    report_data = []
    for file_path in json_files:
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
                report_data.append(data)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {file_path}")
                continue

    if not report_data:
        print("No data found to generate a report.")
        return

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Model Evaluation Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f9; color: #333; }
            h1 { text-align: center; color: #444; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; border: 1px solid #ddd; text-align: left; cursor: pointer; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            tr:hover { background-color: #f1f1f1; }
            .container { max-width: 1200px; margin: auto; background: #fff; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Model Evaluation Report</h1>
            <table id="reportTable">
                <thead>
                    <tr>
                        <th onclick="sortTable(0)">Model</th>
                        <th onclick="sortTable(1)">Timestamp</th>
                        <th onclick="sortTable(2)">Eval Name</th>
                        <th onclick="sortTable(3)">Score</th>
                    </tr>
                </thead>
                <tbody>
    """

    for item in report_data:
        model = item.get('eval', {}).get('model', 'N/A')
        timestamp = item.get('eval', {}).get('created', 'N/A')
        eval_name = item.get('eval', {}).get('task', 'N/A')
        
        score_val = 'Error'
        if item.get('status') != 'error':
            try:
                score_val = item['results']['scores'][0]['metrics']['accuracy']['value']
                score_display = f"{score_val:.4f}"
            except (KeyError, IndexError):
                score_display = 'N/A'
        else:
            score_display = 'Error'

        html_content += f"""
                    <tr>
                        <td>{model}</td>
                        <td>{timestamp}</td>
                        <td>{eval_name}</td>
                        <td>{score_display}</td>
                    </tr>
        """

    html_content += """
                </tbody>
            </table>
        </div>
        <script>
            function sortTable(n) {
                var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
                table = document.getElementById("reportTable");
                switching = true;
                dir = "asc";
                while (switching) {
                    switching = false;
                    rows = table.rows;
                    for (i = 1; i < (rows.length - 1); i++) {
                        shouldSwitch = false;
                        x = rows[i].getElementsByTagName("TD")[n];
                        y = rows[i + 1].getElementsByTagName("TD")[n];

                        let xContent = x.innerText || x.textContent;
                        let yContent = y.innerText || y.textContent;

                        // Special handling for timestamp column (index 1)
                        if (n === 1) {
                            xContent = new Date(xContent).getTime();
                            yContent = new Date(yContent).getTime();
                        } else {
                            // Try numeric comparison for score
                            let xNum = parseFloat(xContent);
                            let yNum = parseFloat(yContent);
                            if (!isNaN(xNum) && !isNaN(yNum)) {
                                xContent = xNum;
                                yContent = yNum;
                            }
                        }

                        if (dir === "asc") {
                            if (xContent > yContent) {
                                shouldSwitch = true;
                                break;
                            }
                        } else if (dir === "desc") {
                            if (xContent < yContent) {
                                shouldSwitch = true;
                                break;
                            }
                        }
                    }
                    if (shouldSwitch) {
                        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                        switching = true;
                        switchcount++;
                    } else {
                        if (switchcount === 0 && dir === "asc") {
                            dir = "desc";
                            switching = true;
                        }
                    }
                }
            }
        </script>
    </body>
    </html>
    """

    output_path = 'docs/index.html'
    with open(output_path, 'w') as f:
        f.write(html_content)
    print(f"Report generated at {output_path}")

if __name__ == "__main__":
    generate_html_report()
