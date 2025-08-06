
import React, { useState, useEffect } from 'react';
import './ReportPage.css';

const ReportPage = () => {
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedEval, setSelectedEval] = useState('');
  const [expandedRow, setExpandedRow] = useState(null);

  useEffect(() => {
    // In a real app, this would fetch from an API
    // For now, we'll load from the local JSON file
    fetch('/database.json')
      .then(response => response.json())
      .then(jsonData => {
        setData(jsonData);
        setFilteredData(jsonData);
      })
      .catch(error => console.error('Error loading data:', error));
  }, []);

  useEffect(() => {
    let result = data;
    
    // Apply search filter
    if (searchTerm) {
      result = result.filter(item => {
        return (
          item.model.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.eval_name.toLowerCase().includes(searchTerm.toLowerCase())
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
    
    setFilteredData(result);
  }, [searchTerm, selectedModel, selectedEval, data]);

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
    
    const sortedData = [...filteredData].sort((a, b) => {
      let aValue = a[key];
      let bValue = b[key];
      
      // Special handling for timestamp column
      if (key === 'timestamp') {
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
        return direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
    
    setFilteredData(sortedData);
  };

  // Get unique models and evals for filter dropdowns
  const uniqueModels = [...new Set(data.map(item => item.model))];
  const uniqueEvals = [...new Set(data.map(item => item.eval_name))];

  const toggleRowExpansion = (index) => {
    setExpandedRow(expandedRow === index ? null : index);
  };

  return (
    <div className="report-container">
      <h1>Model Evaluation Report</h1>
      
      <div className="filters">
        <div className="search-container">
          <input
            type="text"
            placeholder="Search models or evals..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        
        <div className="filter-dropdowns">
          <select 
            value={selectedModel} 
            onChange={(e) => setSelectedModel(e.target.value)}
          >
            <option value="">All Models</option>
            {uniqueModels.map(model => (
              <option key={model} value={model}>{model}</option>
            ))}
          </select>
          
          <select 
            value={selectedEval} 
            onChange={(e) => setSelectedEval(e.target.value)}
          >
            <option value="">All Evals</option>
            {uniqueEvals.map(evalName => (
              <option key={evalName} value={evalName}>{evalName}</option>
            ))}
          </select>
          
          <button onClick={() => {
            setSearchTerm('');
            setSelectedModel('');
            setSelectedEval('');
          }}>
            Clear Filters
          </button>
        </div>
      </div>
      
      <div className="results-info">
        Showing {filteredData.length} of {data.length} results
      </div>
      
      <table className="report-table">
        <thead>
          <tr>
            <th onClick={() => handleSort('model')}>Model</th>
            <th onClick={() => handleSort('timestamp')}>Timestamp</th>
            <th onClick={() => handleSort('eval_name')}>Eval Name</th>
            <th onClick={() => handleSort('score')}>Score</th>
            <th onClick={() => handleSort('total_tokens')}>Total Tokens</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          {filteredData.map((item, index) => (
            <React.Fragment key={index}>
              <tr>
                <td>{item.model}</td>
                <td>{new Date(item.timestamp).toLocaleString()}</td>
                <td>{item.eval_name}</td>
                <td>{typeof item.score === 'number' ? item.score.toFixed(4) : item.score}</td>
                <td>{item.total_tokens?.toLocaleString()}</td>
                <td>
                  <button onClick={() => toggleRowExpansion(index)}>
                    {expandedRow === index ? 'Hide' : 'Show'} Details
                  </button>
                </td>
              </tr>
              {expandedRow === index && (
                <tr className="details-row">
                  <td colSpan="6">
                    <div className="details-content">
                      <div className="metrics-grid">
                        <div className="metric-card">
                          <h4>Token Usage</h4>
                          <p>Input: {item.total_input_tokens?.toLocaleString()}</p>
                          <p>Output: {item.total_output_tokens?.toLocaleString()}</p>
                          <p>Total: {item.total_tokens?.toLocaleString()}</p>
                        </div>
                        
                        <div className="metric-card">
                          <h4>Primary Metrics</h4>
                          <p>Score: {typeof item.score === 'number' ? item.score.toFixed(4) : item.score}</p>
                          {item.additional_metrics?.stderr !== undefined && (
                            <p>Std Error: {item.additional_metrics.stderr.toFixed(6)}</p>
                          )}
                        </div>
                        
                        {Object.keys(item.additional_metrics || {}).length > 0 && (
                          <div className="metric-card">
                            <h4>Additional Metrics</h4>
                            {Object.entries(item.additional_metrics).map(([key, value]) => (
                              <p key={key}>
                                {key}: {typeof value === 'number' ? value.toFixed(6) : value}
                              </p>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ReportPage;
