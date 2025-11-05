import React, { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult("");
    setError("");
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    setError("");
    setResult("");

    try {
      const response = await fetch(
        "https://resume-parser-backend-i8qf.onrender.com/extract_skills",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("Failed to extract data from resume.");
      }

      const data = await response.json();
      setResult(data.skills || data.summary || JSON.stringify(data, null, 2));
    } catch (err) {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="header">
        <h1>📄 Resume Parser</h1>
        <p>Upload your resume and extract skills automatically.</p>
      </header>

      <div className="upload-section">
        <input type="file" accept=".pdf,.doc,.docx" onChange={handleFileChange} />
        <button onClick={handleUpload} disabled={loading}>
          {loading ? "Processing..." : "Upload & Extract"}
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="result-box">
          <h3>Extracted Skills:</h3>
          <pre>{result}</pre>
        </div>
      )}

      <footer>
        <p>Created Using Flask and React</p>
      </footer>
    </div>
  );
}

export default App;
