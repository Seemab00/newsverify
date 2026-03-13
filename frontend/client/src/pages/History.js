import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaHistory, FaExternalLinkAlt, FaTrash } from 'react-icons/fa';
import { Link } from 'react-router-dom';

function History() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/reports/recent?limit=20');
      setReports(response.data.reports || []);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch history');
      setLoading(false);
    }
  };

  const deleteReport = async (reportId) => {
    if (window.confirm('Are you sure you want to delete this report?')) {
      try {
        await axios.delete(`http://localhost:8000/api/reports/${reportId}`);
        fetchHistory();
      } catch (err) {
        setError('Failed to delete report');
      }
    }
  };

  const getBadgeClass = (verdict) => {
    const classes = {
      'VERIFIED_TRUE': 'badge-verified-true',
      'LIKELY_TRUE': 'badge-likely-true',
      'UNCERTAIN': 'badge-uncertain',
      'LIKELY_FAKE': 'badge-likely-fake',
      'VERIFIED_FAKE': 'badge-verified-fake',
      'UNSAFE': 'badge-unsafe'
    };
    return classes[verdict] || 'badge-secondary';
  };

  if (loading) {
    return (
      <div className="spinner-container">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <h2 className="mb-4">
        <FaHistory className="me-2" />
        Verification History
      </h2>

      {error && (
        <div className="alert alert-danger">{error}</div>
      )}

      {reports.length === 0 ? (
        <div className="alert alert-info">
          No verification history yet. Try verifying some news!
        </div>
      ) : (
        <div className="row">
          {reports.map((report) => (
            <div key={report.report_id} className="col-md-6 mb-3">
              <div className="card h-100">
                <div className="card-body">
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <h5 className="card-title text-truncate" style={{ maxWidth: '70%' }}>
                      {report.title || 'No title'}
                    </h5>
                    <span className={`badge ${getBadgeClass(report.final_verdict)}`}>
                      {report.final_verdict}
                    </span>
                  </div>
                  
                  <p className="card-text text-muted small">
                    <strong>Domain:</strong> {report.domain}<br />
                    <strong>Score:</strong> {report.trust_score}%<br />
                    <strong>Date:</strong> {new Date(report.timestamp).toLocaleString()}
                  </p>
                  
                  <div className="d-flex justify-content-between align-items-center">
                    <a href={report.url} target="_blank" rel="noopener noreferrer" 
                       className="btn btn-sm btn-outline-primary">
                      <FaExternalLinkAlt className="me-1" /> Original
                    </a>
                    <div>
                      <Link to={`/report/${report.report_id}`} 
                            className="btn btn-sm btn-primary me-2">
                        View Report
                      </Link>
                      <button 
                        onClick={() => deleteReport(report.report_id)}
                        className="btn btn-sm btn-danger">
                        <FaTrash />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default History;