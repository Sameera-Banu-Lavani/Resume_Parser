import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!file) {
      alert('Please select a file!');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://127.0.0.1:5000/parse', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setResult(data.text || 'No text found');
    } catch (error) {
      console.error('Error:', error);
      setResult('Error connecting to backend');
    }
  };

  return (
    <div className="App">
      <h1>Resume Parser</h1>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleSubmit}>Parse Resume</button>
      <pre>{result}</pre>
    </div>
  );
}

export default App;
