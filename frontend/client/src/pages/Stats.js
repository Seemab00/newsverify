import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaChartBar, FaCheckCircle, FaExclamationTriangle, FaShieldAlt } from 'react-icons/fa';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

function Stats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/stats');
      setStats(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch statistics');
      setLoading(false);
    }
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

  // Pie chart data for verdict distribution
  const pieData = {
    labels: stats?.verdict_distribution ? Object.keys(stats.verdict_distribution) : [],
    datasets: [
      {
        data: stats?.verdict_distribution ? Object.values(stats.verdict_distribution) : [],
        backgroundColor: [
          '#28a745', '#5cb85c', '#ffc107', '#dc3545', '#721c24', '#343a40'
        ],
        borderWidth: 1,
      },
    ],
  };

  // Bar chart data for daily verifications
  const barData = {
    labels: ['Today', 'This Week', 'This Month'],
    datasets: [
      {
        label: 'Verifications',
        data: [
          stats?.today_verifications || 0,
          stats?.weekly_verifications || 0,
          stats?.total_verifications || 0
        ],
        backgroundColor: '#007bff',
      },
    ],
  };

  return (
    <div className="fade-in">
      <h2 className="mb-4">
        <FaChartBar className="me-2" />
        Statistics Dashboard
      </h2>

      {error && (
        <div className="alert alert-danger">{error}</div>
      )}

      {/* Summary Cards */}
      <div className="row mb-4">
        <div className="col-md-4 mb-3">
          <div className="card text-center bg-primary text-white">
            <div className="card-body">
              <FaCheckCircle size={40} className="mb-2" />
              <h3>{stats?.total_verifications || 0}</h3>
              <p className="mb-0">Total Verifications</p>
            </div>
          </div>
        </div>
        <div className="col-md-4 mb-3">
          <div className="card text-center bg-success text-white">
            <div className="card-body">
              <FaShieldAlt size={40} className="mb-2" />
              <h3>{stats?.today_verifications || 0}</h3>
              <p className="mb-0">Today's Verifications</p>
            </div>
          </div>
        </div>
        <div className="col-md-4 mb-3">
          <div className="card text-center bg-warning text-white">
            <div className="card-body">
              <FaExclamationTriangle size={40} className="mb-2" />
              <h3>
                {(stats?.verdict_distribution?.LIKELY_FAKE || 0) + 
                 (stats?.verdict_distribution?.VERIFIED_FAKE || 0)}
              </h3>
              <p className="mb-0">Fake News Detected</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="row">
        <div className="col-md-6 mb-4">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Verdict Distribution</h5>
            </div>
            <div className="card-body">
              {pieData.labels.length > 0 ? (
                <Pie data={pieData} />
              ) : (
                <p className="text-center text-muted my-5">No data available</p>
              )}
            </div>
          </div>
        </div>
        <div className="col-md-6 mb-4">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Verification Trends</h5>
            </div>
            <div className="card-body">
              <Bar 
                data={barData}
                options={{
                  responsive: true,
                  plugins: {
                    legend: {
                      position: 'top',
                    },
                    title: {
                      display: false,
                    },
                  },
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Database Info */}
      <div className="card">
        <div className="card-header">
          <h5 className="mb-0">Database Information</h5>
        </div>
        <div className="card-body">
          <p><strong>Database:</strong> {stats?.database || 'N/A'}</p>
          <p><strong>Collections:</strong> {stats?.collections?.join(', ') || 'N/A'}</p>
          <p><strong>Status:</strong> {stats?.connected ? '✅ Connected' : '❌ Disconnected'}</p>
        </div>
      </div>
    </div>
  );
}

export default Stats;