import React, { useState } from 'react';
import UploadBox from '../components/UploadBox';
import ResultCard from '../components/ResultCard';

function Home() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleProcess = async (transcript, file) => {
    setLoading(true);
    setError('');
    try {
      let finalTranscript = transcript;

      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch('http://localhost:8000/api/v1/transcribe', {
          method: 'POST',
          body: formData,
        });
        if (!res.ok) throw new Error('Transcription failed');
        const data = await res.json();
        finalTranscript = data.transcript;
      }

      if (!finalTranscript) {
        throw new Error('No transcript to summarize');
      }

      const sumRes = await fetch('http://localhost:8000/api/v1/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ transcript: finalTranscript }),
      });

      if (!sumRes.ok) throw new Error('Summarization failed');
      const sumData = await sumRes.json();
      setResult(sumData);
    } catch (err) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-page">
      {error && <div className="error-message">{error}</div>}
      
      {loading ? (
        <div className="card loading-spinner">
          <h2>Processing with AI...</h2>
          <p>This may take a minute depending on the length of your meeting.</p>
        </div>
      ) : result ? (
        <div>
          <button className="btn-secondary" onClick={() => setResult(null)} style={{marginBottom: '1rem'}}>
            &larr; Summarize Another Meeting
          </button>
          <ResultCard result={result} />
        </div>
      ) : (
        <UploadBox onProcess={handleProcess} />
      )}
    </div>
  );
}

export default Home;
