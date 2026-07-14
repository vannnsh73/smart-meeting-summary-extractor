import React, { useState, useEffect } from 'react';
import ResultCard from '../components/ResultCard';

const API_BASE = 'http://localhost:8000/api/v1';

function History() {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    fetchMeetings();
  }, []);

  const fetchMeetings = async () => {
    try {
      const res = await fetch(`${API_BASE}/meetings`);
      if (!res.ok) throw new Error('Failed to fetch meetings');
      setMeetings(await res.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this meeting?')) return;
    try {
      const res = await fetch(`${API_BASE}/meetings/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Failed to delete');
      setMeetings(prev => prev.filter(m => m.id !== id));
    } catch (err) {
      alert(err.message);
    }
  };

  if (loading) return <div className="loading-spinner"><p className="body-lg">Loading history...</p></div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="history-page">
      <h1 className="headline-md" style={{ marginBottom: '32px' }}>Meeting History</h1>

      {meetings.length === 0 ? (
        <div className="card">
          <p className="body-md text-muted">No meetings saved yet.</p>
        </div>
      ) : (
        meetings.map(meeting => (
          <div key={meeting.id} style={{ marginBottom: '16px' }}>
            <div
              className="card"
              style={{ marginBottom: expandedId === meeting.id ? '0' : '0', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
              onClick={() => setExpandedId(expandedId === meeting.id ? null : meeting.id)}
            >
              <div>
                <h3 className="label-md" style={{ margin: '0 0 4px 0' }}>{meeting.title || 'Untitled Meeting'}</h3>
                <small className="body-sm text-muted">
                  {new Date(meeting.created_at).toLocaleString()}
                </small>
              </div>
              <button
                className="btn-secondary"
                style={{ color: 'var(--priority-high)', borderColor: 'var(--priority-high)' }}
                onClick={(e) => handleDelete(meeting.id, e)}
              >
                Delete
              </button>
            </div>

            {expandedId === meeting.id && (
              <div style={{ marginTop: '16px' }}>
                <ResultCard result={meeting} />
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}

export default History;

