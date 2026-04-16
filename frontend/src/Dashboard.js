import React, { useState, useEffect } from 'react';
import './Dashboard.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

function Dashboard({ onLogout }) {
  const [pipelines, setPipelines] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('ALL');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    pipeline_type: 'training',
    created_by: 'admin'
  });

  useEffect(() => {
    fetchPipelines();
    fetchSummary();
    const interval = setInterval(() => {
      fetchPipelines();
      fetchSummary();
    }, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [filter]);

  const fetchPipelines = async () => {
    try {
      const url = filter === 'ALL' 
        ? `${API_BASE}/pipelines`
        : `${API_BASE}/pipelines?state=${filter}`;
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setPipelines(data);
      }
    } catch (error) {
      console.error('Error fetching pipelines:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await fetch(`${API_BASE}/dashboard/summary`);
      if (response.ok) {
        const data = await response.json();
        setSummary(data);
      }
    } catch (error) {
      console.error('Error fetching summary:', error);
    }
  };

  const handleCreatePipeline = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE}/pipelines`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      if (response.ok) {
        setFormData({ name: '', description: '', pipeline_type: 'training', created_by: 'admin' });
        setShowCreateForm(false);
        fetchPipelines();
        fetchSummary();
      }
    } catch (error) {
      console.error('Error creating pipeline:', error);
    }
  };

  const handleStateChange = async (pipelineId, newState, reason) => {
    try {
      const response = await fetch(`${API_BASE}/pipelines/${pipelineId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_state: newState,
          transition_reason: reason,
          triggered_by: 'admin'
        }),
      });
      if (response.ok) {
        fetchPipelines();
        fetchSummary();
      }
    } catch (error) {
      console.error('Error updating pipeline:', error);
    }
  };

  const getStateColor = (state) => {
    const colors = {
      'PENDING': '#fbbf24',
      'RUNNING': '#3b82f6',
      'COMPLETED': '#10b981',
      'FAILED': '#ef4444',
      'CANCELLED': '#6b7280'
    };
    return colors[state] || '#6b7280';
  };

  const getStateIcon = (state) => {
    const icons = {
      'PENDING': '⏱️',
      'RUNNING': '▶️',
      'COMPLETED': '✓',
      'FAILED': '✕',
      'CANCELLED': '⊘'
    };
    return icons[state] || '•';
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>🚀 Rubiscape ML Pipeline Tracker</h1>
          <button onClick={onLogout} className="btn btn-logout">Logout</button>
        </div>
      </header>

      {summary && (
        <div className="summary-section">
          <div className="summary-grid">
            <div className="summary-card total">
              <div className="summary-value">{summary.total}</div>
              <div className="summary-label">Total Pipelines</div>
            </div>
            <div className="summary-card pending">
              <div className="summary-value">{summary.pending}</div>
              <div className="summary-label">Pending</div>
            </div>
            <div className="summary-card running">
              <div className="summary-value">{summary.running}</div>
              <div className="summary-label">Running</div>
            </div>
            <div className="summary-card completed">
              <div className="summary-value">{summary.completed}</div>
              <div className="summary-label">Completed</div>
            </div>
            <div className="summary-card failed">
              <div className="summary-value">{summary.failed}</div>
              <div className="summary-label">Failed</div>
            </div>
            <div className="summary-card success-rate">
              <div className="summary-value">{summary.success_rate.toFixed(1)}%</div>
              <div className="summary-label">Success Rate</div>
            </div>
          </div>
        </div>
      )}

      <div className="controls-section">
        <div className="filter-buttons">
          <button 
            className={`filter-btn ${filter === 'ALL' ? 'active' : ''}`}
            onClick={() => setFilter('ALL')}
          >
            All
          </button>
          <button 
            className={`filter-btn ${filter === 'PENDING' ? 'active' : ''}`}
            onClick={() => setFilter('PENDING')}
          >
            Pending
          </button>
          <button 
            className={`filter-btn ${filter === 'RUNNING' ? 'active' : ''}`}
            onClick={() => setFilter('RUNNING')}
          >
            Running
          </button>
          <button 
            className={`filter-btn ${filter === 'COMPLETED' ? 'active' : ''}`}
            onClick={() => setFilter('COMPLETED')}
          >
            Completed
          </button>
          <button 
            className={`filter-btn ${filter === 'FAILED' ? 'active' : ''}`}
            onClick={() => setFilter('FAILED')}
          >
            Failed
          </button>
        </div>
        <button 
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="btn btn-primary"
        >
          {showCreateForm ? '✕ Cancel' : '+ New Pipeline'}
        </button>
      </div>

      {showCreateForm && (
        <form onSubmit={handleCreatePipeline} className="create-form">
          <div className="form-group">
            <label>Pipeline Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              placeholder="e.g., Data Ingestion Pipeline"
              required
            />
          </div>
          <div className="form-group">
            <label>Description</label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Pipeline description"
            />
          </div>
          <div className="form-group">
            <label>Type</label>
            <select
              value={formData.pipeline_type}
              onChange={(e) => setFormData({...formData, pipeline_type: e.target.value})}
            >
              <option value="data_ingestion">Data Ingestion</option>
              <option value="training">Training</option>
              <option value="deployment">Deployment</option>
            </select>
          </div>
          <button type="submit" className="btn btn-primary">Create Pipeline</button>
        </form>
      )}

      <main className="dashboard-content">
        {loading ? (
          <div className="loading">Loading pipelines...</div>
        ) : pipelines.length === 0 ? (
          <div className="empty-state">
            <p>No pipelines found</p>
            <button onClick={() => setShowCreateForm(true)} className="btn btn-secondary">
              Create your first pipeline
            </button>
          </div>
        ) : (
          <div className="pipelines-grid">
            {pipelines.map((pipeline) => (
              <div key={pipeline.id} className="pipeline-card">
                <div className="pipeline-header">
                  <div className="pipeline-title">
                    <h3>{pipeline.name}</h3>
                    <span className="pipeline-type">{pipeline.pipeline_type.replace('_', ' ')}</span>
                  </div>
                  <div 
                    className="pipeline-state"
                    style={{backgroundColor: getStateColor(pipeline.current_state)}}
                  >
                    <span className="state-icon">{getStateIcon(pipeline.current_state)}</span>
                    <span className="state-text">{pipeline.current_state}</span>
                  </div>
                </div>
                
                {pipeline.description && (
                  <p className="pipeline-description">{pipeline.description}</p>
                )}
                
                <div className="pipeline-meta">
                  <div><strong>Created by:</strong> {pipeline.created_by}</div>
                  <div><strong>Created:</strong> {new Date(pipeline.created_at).toLocaleDateString()}</div>
                </div>

                <div className="pipeline-actions">
                  <button 
                    className="action-btn state-btn"
                    onClick={() => handleStateChange(pipeline.id, 'RUNNING', 'Started by user')}
                    disabled={pipeline.current_state === 'RUNNING'}
                  >
                    Start
                  </button>
                  <button 
                    className="action-btn state-btn"
                    onClick={() => handleStateChange(pipeline.id, 'COMPLETED', 'Completed by user')}
                    disabled={pipeline.current_state === 'COMPLETED'}
                  >
                    Complete
                  </button>
                  <button 
                    className="action-btn state-btn fail"
                    onClick={() => handleStateChange(pipeline.id, 'FAILED', 'Failed by user')}
                    disabled={pipeline.current_state === 'FAILED'}
                  >
                    Fail
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default Dashboard;
