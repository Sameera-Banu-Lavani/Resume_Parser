import React, { useState, useCallback } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");
  const [error, setError] = useState("");

  const handleFileChange = useCallback((e) => {
    const selectedFile = e.target.files[0];

    if (selectedFile) {
      const allowedTypes = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      ];
      if (!allowedTypes.includes(selectedFile.type)) {
        setError("Please select a valid file format (PDF, DOC, or DOCX)");
        setFile(null);
        return;
      }

      if (selectedFile.size > 10 * 1024 * 1024) {
        setError("File size must be less than 10MB");
        setFile(null);
        return;
      }
    }

    setFile(selectedFile);
    setResult("");
    setError("");
  }, []);

  const handleUpload = useCallback(async () => {
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
        const errorText = await response.text();
        throw new Error(
          `Failed to extract data from resume: ${response.status} ${errorText}`
        );
      }

      const data = await response.json();

      if (
        !data ||
        (!data.skills && !data.summary && Object.keys(data).length === 0)
      ) {
        setError("No skills or data could be extracted from the resume.");
        return;
      }

      setResult(data.skills || data.summary || JSON.stringify(data, null, 2));
    } catch (err) {
      console.error("Upload error:", err);
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [file]);

  return (
    <div className="App">
      <header className="header">
        <h1>📄 Resume Parser</h1>
        <p>Upload your resume and extract skills automatically.</p>
      </header>

      <div className="upload-section">
        <label htmlFor="file-input" className="file-label">
          Choose Resume File (PDF, DOC, DOCX - Max 10MB)
        </label>
        <input
          id="file-input"
          type="file"
          accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={handleFileChange}
          disabled={loading}
          aria-describedby="file-error"
        />
        {file && (
          <p className="selected-file">
            Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
          </p>
        )}
        <button
          onClick={handleUpload}
          disabled={loading || !file}
          aria-label={
            loading
              ? "Processing resume"
              : "Upload and extract skills from resume"
          }
        >
          {loading ? "Processing..." : "Upload & Extract"}
        </button>
      </div>

      {error && (
        <div className="error" role="alert" id="file-error" aria-live="polite">
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div
          className="result-box"
          role="region"
          aria-labelledby="result-title"
        >
          <h3 id="result-title">Extracted Skills:</h3>
          <pre aria-label="Extracted skills data">{result}</pre>
        </div>
      )}

      <footer>
        <p>Created Using Flask and React</p>
      </footer>
    </div>
  );
}

export default App;
