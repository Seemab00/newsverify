import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import { FaShieldAlt, FaHistory, FaChartBar, FaHome } from 'react-icons/fa';
import Home from './pages/Home';
import History from './pages/History';
import Stats from './pages/Stats';
import Report from './pages/Report';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        {/* Navigation Bar */}
        <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
          <div className="container">
            <Link className="navbar-brand" to="/">
              <FaShieldAlt className="me-2" />
              NewsVerify
            </Link>
            <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
              <span className="navbar-toggler-icon"></span>
            </button>
            <div className="collapse navbar-collapse" id="navbarNav">
              <ul className="navbar-nav ms-auto">
                <li className="nav-item">
                  <Link className="nav-link" to="/">
                    <FaHome className="me-1" /> Home
                  </Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/history">
                    <FaHistory className="me-1" /> History
                  </Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/stats">
                    <FaChartBar className="me-1" /> Statistics
                  </Link>
                </li>
              </ul>
            </div>
          </div>
        </nav>

        {/* Routes */}
        <div className="container mt-4">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/history" element={<History />} />
            <Route path="/stats" element={<Stats />} />
            <Route path="/report/:id" element={<Report />} />
          </Routes>
        </div>

        {/* Footer */}
        <footer className="bg-light text-center text-muted py-3 mt-5">
          <div className="container">
            © 2026 NewsVerify - AI-Powered News Verification System
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;