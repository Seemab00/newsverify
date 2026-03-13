import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { FaArrowLeft, FaShare, FaShieldAlt, FaRobot, FaNewspaper, FaGlobe } from 'react-icons/fa';

function Report() {
  const { id } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [shareText, setShareText] = useState('');

  useEffect(() => {
    fetchReport();
  }, [id]);

  const fetchReport = async () => {
    try {
      const response = await axios.get(`https://newsverify-production.up.railway.app/api/reports/${id}`);
      setReport(response.data);
      
      const shareResponse = await axios.post('https://newsverify-production.up.railway.app/api/share', response.data);
      setShareText(shareResponse.data.shareable);
      
      setLoading(false);
    } catch (err) {
      setError('Report not found');
      setLoading(false);
    }
  };

  const getScoreClass = (score) => {
    if (score >= 80) return 'score-high';
    if (score >= 60) return 'score-medium';
    return 'score-low';
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

  const copyToClipboard = () => {
    navigator.clipboard.writeText(shareText);
    alert('Shareable text copied to clipboard!');
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

  if (error) {
    return (
      <div className="alert alert-danger">
        {error}
        <br />
        <Link to="/" className="btn btn-primary mt-3">
          <FaArrowLeft className="me-2" />
          Back to Home
        </Link>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <div className="mb-3">
        <Link to="/history" className="btn btn-outline-primary">
          <FaArrowLeft className="me-2" />
          Back to History
        </Link>
      </div>

      {/* Header */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="d-flex justify-content-between align-items-start">
            <div>
              <h2>Verification Report</h2>
              <p className="text-muted mb-1">Report ID: {report.report_id}</p>
              <p className="text-muted">Generated: {new Date(report.timestamp).toLocaleString()}</p>
            </div>
            <div className={`badge ${getBadgeClass(report.overall_assessment?.final_verdict)} p-3`}>
              <h5 className="mb-0">{report.overall_assessment?.final_verdict}</h5>
            </div>
          </div>
        </div>
      </div>

      {/* Overall Score */}
      <div className="card mb-4 text-center">
        <div className="card-body">
          <h4>Overall Trust Score</h4>
          <div className={`score-circle ${getScoreClass(report.overall_assessment?.trust_score)}`}>
            {report.overall_assessment?.trust_score}%
          </div>
          <p className="lead">{report.overall_assessment?.summary}</p>
        </div>
      </div>

      {/* Details Grid */}
      <div className="row">
        {/* Security Check */}
        <div className="col-md-6 mb-4">
          <div className="card h-100">
            <div className="card-header bg-primary text-white">
              <FaShieldAlt className="me-2" />
              Security Check
            </div>
            <div className="card-body">
              <p><strong>Status:</strong> {report.details?.security?.verdict}</p>
              <p><strong>Safety Score:</strong> {report.details?.security?.score}%</p>
              <p><strong>Threats Detected:</strong> {report.details?.security?.threats?.malicious || 0}</p>
            </div>
          </div>
        </div>

        {/* Content Info */}
        <div className="col-md-6 mb-4">
          <div className="card h-100">
            <div className="card-header bg-success text-white">
              <FaNewspaper className="me-2" />
              Content Information
            </div>
            <div className="card-body">
              <p><strong>Title:</strong> {report.details?.content?.title}</p>
              <p><strong>Domain:</strong> {report.details?.content?.domain}</p>
              <p><strong>Authors:</strong> {report.details?.content?.authors?.join(', ') || 'Unknown'}</p>
              <p><strong>Word Count:</strong> {report.details?.content?.word_count}</p>
            </div>
          </div>
        </div>

        {/* AI Analysis */}
        <div className="col-md-6 mb-4">
          <div className="card h-100">
            <div className="card-header bg-info text-white">
              <FaRobot className="me-2" />
              AI Analysis
            </div>
            <div className="card-body">
              <p><strong>Fake Probability:</strong> {report.details?.ai_analysis?.fake_probability}%</p>
              <p><strong>Bias Score:</strong> {report.details?.ai_analysis?.bias_score}%</p>
              <p><strong>Sensationalism:</strong> {report.details?.ai_analysis?.sensationalism}%</p>
              {report.details?.ai_analysis?.red_flags?.length > 0 && (
                <>
                  <p><strong>Red Flags:</strong></p>
                  <ul>
                    {report.details.ai_analysis.red_flags.map((flag, i) => (
                      <li key={i}>{flag}</li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Source Verification */}
        <div className="col-md-6 mb-4">
          <div className="card h-100">
            <div className="card-header bg-warning text-white">
              <FaGlobe className="me-2" />
              Source Verification
            </div>
            <div className="card-body">
              <p><strong>Consistency Score:</strong> {report.details?.source_verification?.consistency_score}%</p>
              <p><strong>Trusted Sources:</strong> {report.details?.source_verification?.trusted_sources}</p>
              <p><strong>Total Sources:</strong> {report.details?.source_verification?.total_sources}</p>
              <p><strong>Consensus:</strong> {report.details?.source_verification?.consensus}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="card mb-4 bg-light">
        <div className="card-header">
          <h5 className="mb-0">Recommendations</h5>
        </div>
        <div className="card-body">
          <ul className="list-unstyled">
            {report.recommendations?.map((rec, i) => (
              <li key={i} className="mb-2">• {rec}</li>
            ))}
          </ul>
        </div>
      </div>

      {/* Share Section */}
      <div className="card">
        <div className="card-header">
          <h5 className="mb-0">Share Report</h5>
        </div>
        <div className="card-body">
          <pre className="bg-light p-3 rounded" style={{ whiteSpace: 'pre-wrap' }}>
            {shareText}
          </pre>
          <button className="btn btn-primary mt-2" onClick={copyToClipboard}>
            <FaShare className="me-2" />
            Copy Shareable Text
          </button>
        </div>
      </div>
    </div>
  );
}

export default Report;