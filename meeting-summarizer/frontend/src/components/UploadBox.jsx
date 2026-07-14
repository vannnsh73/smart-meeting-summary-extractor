import React, { useState } from 'react';

function UploadBox({ onProcess }) {
  const [transcript, setTranscript] = useState('');
  const [file, setFile] = useState(null);

  const handleSubmit = () => {
    if (!transcript.trim() && !file) {
      alert('Please provide a transcript or upload an audio file.');
      return;
    }
    onProcess(transcript, file);
  };

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      const validTypes = ['audio/mpeg', 'audio/wav', 'audio/x-m4a', 'audio/mp4'];
      // Accept simple extensions if mime type is missing
      if (selected.name.match(/\.(mp3|wav|m4a)$/i) || validTypes.includes(selected.type)) {
        setFile(selected);
      } else {
        alert('Invalid file format. Please upload .mp3, .wav, or .m4a');
        e.target.value = null;
      }
    }
  };

  return (
    <div className="card upload-box">
      <h2 className="headline-md">Upload Meeting</h2>
      <p className="body-md text-muted" style={{ marginBottom: '1.5rem' }}>
        Paste a transcript or upload an audio recording to get started.
      </p>
      
      <textarea 
        placeholder="Paste your meeting transcript here..."
        value={transcript}
        onChange={(e) => setTranscript(e.target.value)}
        disabled={!!file}
      />
      
      <div className="divider">OR</div>
      
      <div style={{ marginBottom: '1.5rem' }}>
        <input 
          type="file" 
          accept=".mp3,.wav,.m4a,audio/mpeg,audio/wav,audio/x-m4a" 
          onChange={handleFileChange}
          disabled={transcript.trim().length > 0}
        />
        <small className="label-md text-muted" style={{ display: 'block', marginTop: '0.5rem' }}>
          Accepted formats: .mp3, .wav, .m4a
        </small>
      </div>

      <button className="btn-primary" onClick={handleSubmit} style={{ width: '100%' }}>
        Summarize Meeting
      </button>
    </div>
  );
}

export default UploadBox;
