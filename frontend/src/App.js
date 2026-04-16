import React, { useState, useEffect } from 'react';
import Dashboard from './Dashboard';
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(true); // Default to logged in for MVP

  return (
    <div className="App">
      {isLoggedIn ? (
        <Dashboard onLogout={() => setIsLoggedIn(false)} />
      ) : (
        <div className="login-page">
          <div className="login-card">
            <h1 className="title">Rubiscape ML Pipeline Tracker</h1>
            <p className="subtitle">Track your ML pipelines in real-time</p>
            <button 
              onClick={() => setIsLoggedIn(true)} 
              className="btn btn-primary"
            >
              Continue
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
