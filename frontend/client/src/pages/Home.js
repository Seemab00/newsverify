import React, { useState } from 'react';
import axios from 'axios';
import { FaSearch, FaShieldAlt, FaRobot, FaNewspaper, FaChartLine } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';

function Home() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:8000/api/verify', {
        url: url,
        check_deep: true
      });
      
      if (response.data.report?.report_id) {
        navigate(`/report/${response.data.report.report_id}`);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Error verifying news');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in">
      {/* Hero Section */}
      <div className="text-center mb-5">
        <h1 className="display-4 mb-3">
          <FaShieldAlt className="text-primary me-2" />
          NewsVerify
        </h1>
        <p className="lead text-muted">
          AI-Powered News Verification System - Check if news is fake or real
        </p>
      </div>

      {/* Search Form */}
      <div className="row justify-content-center mb-5">
        <div className="col-md-8">
          <div className="card p-4">
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="url" className="form-label fw-bold">
                  Enter News URL
                </label>
                <input
                  type="url"
                  className="form-control form-control-lg"
                  id="url"
                  placeholder="https://example.com/news-article"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  required
                />
                <div className="form-text">
                  Paste any news article link to verify its authenticity
                </div>
              </div>
              <button
                type="submit"
                className="btn btn-primary btn-lg w-100"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" />
                    Verifying...
                  </>
                ) : (
                  <>
                    <FaSearch className="me-2" />
                    Verify News
                  </>
                )}
              </button>
            </form>
            
            {error && (
              <div className="alert alert-danger mt-3">
                {error}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="row mt-5">
        <div className="col-md-3 mb-3">
          <div className="card h-100 text-center p-3">
            <FaShieldAlt className="text-primary fs-1 mb-3" />
            <h5>Security Check</h5>
            <p className="text-muted">Scans URLs for malware and phishing threats</p>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card h-100 text-center p-3">
            <FaNewspaper className="text-success fs-1 mb-3" />
            <h5>Content Extraction</h5>
            <p className="text-muted">Extracts article content automatically</p>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card h-100 text-center p-3">
            <FaRobot className="text-info fs-1 mb-3" />
            <h5>AI Analysis</h5>
            <p className="text-muted">Uses Groq AI to detect fake news patterns</p>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card h-100 text-center p-3">
            <FaChartLine className="text-warning fs-1 mb-3" />
            <h5>Source Verification</h5>
            <p className="text-muted">Checks with multiple trusted sources</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;