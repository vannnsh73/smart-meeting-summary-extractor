import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import History from './pages/History';

function App() {
  return (
    <Router>
      <div className="app-container">
        <nav className="navbar">
          <div className="navbar-brand">
            <Link to="/" className="headline-md" style={{ color: '#f7f9fb', textDecoration: 'none' }}>Smart Meeting Summarizer</Link>
          </div>
          <div className="navbar-links">
            <Link to="/history" className="label-md">History</Link>
          </div>
        </nav>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
