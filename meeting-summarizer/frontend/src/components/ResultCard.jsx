import React, { useState } from 'react';
import ActionTable from './ActionTable';

function ResultCard({ result }) {
  const [emails, setEmails] = useState('');
  const [emailStatus, setEmailStatus] = useState('');
  const [copyStatus, setCopyStatus] = useState('');

  const handleCopy = () => {
    const text = `Summary:\n${result.summary}\n\nDecisions:\n${result.decisions?.join('\n')}`;
    navigator.clipboard.writeText(text);
    setCopyStatus('Copied!');
    setTimeout(() => setCopyStatus(''), 2000);
  };

  const handleDownloadPdf = () => {
    if (!result.id) return;
    window.open(`http://localhost:8000/api/v1/meetings/${result.id}/pdf`, '_blank');
  };

  const handleSendEmail = async () => {
    if (!emails.trim() || !result.id) return;
    setEmailStatus('Sending...');
    
    try {
      const emailList = emails.split(',').map(e => e.trim()).filter(e => e);
      const res = await fetch('http://localhost:8000/api/v1/digest/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ meeting_id: result.id, emails: emailList })
      });
      
      if (!res.ok) throw new Error('Failed to send');
      setEmailStatus('Sent successfully!');
      setEmails('');
    } catch (err) {
      setEmailStatus('Error sending emails');
    }
    
    setTimeout(() => setEmailStatus(''), 3000);
  };

  return (
    <div className="card-cluster">
      <div className="card smart-insight">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 className="headline-md">Executive Summary</h2>
          <button className="btn-secondary" onClick={handleCopy}>
            {copyStatus || 'Copy Summary'}
          </button>
        </div>
        <p className="body-md">{result.summary}</p>
      </div>

      <div className="card">
        <h2 className="headline-md" style={{ marginBottom: '16px' }}>Key Decisions</h2>
        {result.decisions && result.decisions.length > 0 ? (
          <ol className="body-md" style={{ paddingLeft: '1.2rem', margin: 0 }}>
            {result.decisions.map((d, i) => (
              <li key={i} style={{ marginBottom: '8px' }}>{d}</li>
            ))}
          </ol>
        ) : (
          <p className="body-md text-muted">No key decisions recorded.</p>
        )}
      </div>

      <div className="card">
        <h2 className="headline-md" style={{ marginBottom: '16px' }}>Action Items</h2>
        <ActionTable items={result.action_items || []} />
      </div>

      <div className="card" style={{ display: 'flex', gap: '32px', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: '250px' }}>
          <h3 className="headline-md" style={{ fontSize: '18px', marginBottom: '16px' }}>Export Options</h3>
          <button className="btn-primary" onClick={handleDownloadPdf} disabled={!result.id}>
            Download PDF Digest
          </button>
        </div>
        
        <div style={{ flex: 1, minWidth: '300px' }}>
          <h3 className="headline-md" style={{ fontSize: '18px', marginBottom: '16px' }}>Email Participants</h3>
          <div style={{ display: 'flex', gap: '8px' }}>
            <input 
              type="text" 
              placeholder="comma, separated, emails" 
              value={emails}
              onChange={(e) => setEmails(e.target.value)}
              style={{ flex: 1 }}
            />
            <button className="btn-secondary" onClick={handleSendEmail} disabled={!result.id || !emails}>
              Send
            </button>
          </div>
          {emailStatus && <small className="label-md" style={{ display: 'block', marginTop: '8px', color: 'var(--brand-indigo)' }}>{emailStatus}</small>}
        </div>
      </div>
    </div>
  );
}

export default ResultCard;
